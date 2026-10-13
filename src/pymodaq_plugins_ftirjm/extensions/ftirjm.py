# -*- coding: utf-8 -*-
"""Dashboard extension of JM Poumirol's FTIR at CEMES

It shows the images of a camera and moves an Elliptec rotator between two configurable positions. The
instruments come from the Dashboard's experiment: an actuator named ``actuator_name`` and a 2D detector named
``camera_name`` (both in the configuration file of this plugin). Two experiments are shipped in ``resources``:

* ``FTIR_JM``: the Elliptec rotator of ``pymodaq_plugins_thorlabs`` and the PiCamera of ``pymodaq_plugins_raspberry``
* ``FTIR_JM_mock``: the same with Mock plugins, to try the extension without hardware

``main()`` copies them in the experiment folder of PyMoDAQ if they are not there yet.
"""
import shutil
import sys
from pathlib import Path

from qtpy import QtWidgets

from pymodaq_gui import utils as gutils
from pymodaq_gui.plotting.data_viewers.viewer2D import Viewer2D
from pymodaq_gui.utils.widgets import SpinBox
from pymodaq_utils.config import GlobalConfig
from pymodaq_utils.logger import set_logger, get_module_name
from pymodaq_data.data import DataToExport

from pymodaq.utils.config import get_set_experiment_path
from pymodaq.utils.custom_ext import CustomExt
from pymodaq.utils.managers.modules.utils import ModuleType

from pymodaq_plugins_ftirjm.utils import Config as ConfigPlugin

logger = set_logger(get_module_name(__file__))

config = GlobalConfig()
if 'ftirjm' not in config:
    # PyMoDAQ registers the Config of the packages having instrument plugins only (get_instrument_plugins)
    GlobalConfig.register()(ConfigPlugin)


def config_plugin(*args):
    return config('ftirjm', *args)

EXTENSION_NAME = 'FTIR_JM'
CLASS_NAME = 'FTIRJM'

EXPERIMENT_NAME = 'FTIR_JM'
EXPERIMENTS_PATH = Path(__file__).parent.parent.joinpath('resources')


def install_experiments():
    """Copy the experiments shipped with this plugin in PyMoDAQ's experiment folder, if not there yet"""
    for experiment in EXPERIMENTS_PATH.glob(f'{EXPERIMENT_NAME}*.xml'):
        target = get_set_experiment_path().joinpath(experiment.name)
        if not target.exists():
            shutil.copy(experiment, target)
            logger.info(f'Experiment {experiment.stem} copied in {target.parent}')


class FTIRJM(CustomExt):

    params = []

    def __init__(self, parent: gutils.DockArea, dashboard):
        super().__init__(parent, dashboard)  # also creates self.modules_manager for this extension

        self.setup_ui()

    def setup_docks_and_widgets(self):
        self.docks['viewer2D'] = gutils.Dock('Camera')
        self.dockarea.addDock(self.docks['viewer2D'])
        widget = QtWidgets.QWidget()
        self.viewer2D = Viewer2D(widget)
        self.docks['viewer2D'].addWidget(widget)

    def setup_menus_and_toolbars(self, menubar: QtWidgets.QMenuBar = None):
        # adds the toolbar showing/hiding the Dashboard, loading an experiment and a state
        self.create_dashboard_toolbar(add_break=False)

    def setup_actions(self):
        self.add_action('grab', 'Grab', 'camera', "Grab from camera", checkable=True)
        self.add_action('snap', 'Snap', 'snap', "Take a single image from the camera")

        self.add_widget('move1', SpinBox)
        self.get_action('move1').setStyleSheet("background-color : lightgreen; color: black")
        self.get_action('move1').setValue(config_plugin('position_1'))
        self.add_action('move_abs_1', 'Move Abs', 'go_to_1', "Move to the first position")

        self.add_widget('move2', SpinBox)
        self.get_action('move2').setStyleSheet("background-color : lightcoral; color: black")
        self.get_action('move2').setValue(config_plugin('position_2'))
        self.add_action('move_abs_2', 'Move Abs', 'go_to_2', "Move to the second position")

    def connect_things(self):
        self.connect_action('grab', self.grab)
        self.connect_action('snap', self.snap)
        self.connect_action('move_abs_1', lambda: self.move_at(self.get_action('move1').value()))
        self.connect_action('move_abs_2', lambda: self.move_at(self.get_action('move2').value()))

    def do_things_after_ui_setup(self):
        if self.experiment_manager is not None and self.experiment_manager.entry_applied:
            self.connect_camera()

    def do_things_after_experiment_set(self, experiment_name: str, show_dashboard: bool = None):
        """Called each time an experiment has been set in the Dashboard (also from the base class __init__)"""
        super().do_things_after_experiment_set(experiment_name, show_dashboard)
        if hasattr(self, 'viewer2D'):  # else called before setup_ui, done in do_things_after_ui_setup
            self.connect_camera()

    @property
    def camera(self):
        return self.modules_manager.get_mod_from_name(config_plugin('camera_name'), mod=ModuleType.Detector)

    @property
    def actuator(self):
        return self.modules_manager.get_mod_from_name(config_plugin('actuator_name'), mod=ModuleType.Actuator)

    def connect_camera(self):
        """Display the images of the camera of the current experiment"""
        previous_camera = getattr(self, '_camera', None)
        if previous_camera is not None:
            try:
                previous_camera.grab_done_signal.disconnect(self.show_data)
            except (TypeError, RuntimeError):
                pass
        self._camera = self.camera
        if self._camera is None:
            self.update_status(f"No detector named {config_plugin('camera_name')} in the experiment")
        else:
            self._camera.grab_done_signal.connect(self.show_data)

    def grab(self, do_grab: bool):
        if self.camera is None:
            return
        if do_grab:
            self.camera.grab()
        else:
            self.camera.stop_grab()

    def snap(self):
        if self.camera is not None:
            self.camera.snap()

    def move_at(self, value: float):
        if self.actuator is None:
            self.update_status(f"No actuator named {config_plugin('actuator_name')} in the experiment")
        else:
            self.actuator.move_abs(value)

    def show_data(self, dte: DataToExport):
        dwa = dte.get_data_from_dim('Data2D')
        if len(dwa) > 0:
            self.viewer2D.show_data(dwa[0])

    def _quit_fun(self) -> bool:
        if self.camera is not None and self.is_action_checked('grab'):
            self.camera.stop_grab()
        return True


def main():
    """Run the extension on its own: loads a Dashboard (hidden) with the FTIR_JM experiment, then the extension

    The Dashboard command line options apply, for instance ``-x FTIR_JM_mock`` to load the mock experiment.
    """
    from pymodaq_gui.qt_utils import mkQApp
    from pymodaq.dashboard import load_dashboard_with_arguments
    from pymodaq.utils.gui_utils.loader_utils import create_extension

    install_experiments()
    if not any(arg in sys.argv for arg in ('-x', '--experiment')):
        sys.argv.extend(['-x', EXPERIMENT_NAME])

    app = mkQApp('FTIR JM')

    win, dashboard, _ = load_dashboard_with_arguments(show_dashboard=False,
                                                      load_extension=False,
                                                      )
    win.mainwindow.setVisible(False)

    win_ext, ext = create_extension(dashboard, FTIRJM, show_extension=True)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
