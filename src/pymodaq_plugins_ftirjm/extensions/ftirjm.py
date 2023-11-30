from pymodaq.utils import gui_utils as gutils
from pymodaq.utils import daq_utils as utils
from pyqtgraph.parametertree import Parameter, ParameterTree
from pymodaq.utils.parameter import pymodaq_ptypes
from qtpy import QtWidgets, QtCore

from pymodaq.utils.plotting.data_viewers.viewer1D import Viewer1D
from pymodaq.utils.plotting.data_viewers.viewer2D import Viewer2D
from pymodaq.utils.data import DataToExport, DataWithAxes
from pymodaq.utils.gui_utils.widgets import PushButtonIcon, LabelWithFont, SpinBox

config = utils.load_config()
logger = utils.set_logger(utils.get_module_name(__file__))

EXTENSION_NAME = 'FTIR_JM'
CLASS_NAME = 'FTIRJM'


class FTIRJM(gutils.CustomApp):
    # list of dicts enabling the settings tree on the user interface
    params = []

    def __init__(self, dockarea, dashboard):
        super().__init__(dockarea, dashboard)
        self.viewer2D: Viewer2D = None

        self.setup_ui()

    def setup_actions(self):
        self.add_action('quit', 'Quit', 'close2', "Quit program", toolbar=self.toolbar)
        self.add_action('grab', 'Grab', 'camera', "Grab from camera", checkable=True, toolbar=self.toolbar)
        self.add_action('snap', 'Snap', 'snap', "Load target file (.h5, .png, .jpg) or data from camera",
                        checkable=False, toolbar=self.toolbar)
        self.add_action('show', 'Show/hide', 'read2', "Show Hide Dashboard", checkable=True, toolbar=self.toolbar,
                        checked=True)
        self.add_widget('move1', SpinBox)
        self.get_action('move1').setStyleSheet("background-color : lightgreen; color: black")
        self.add_action('move_abs_1', 'Move Abs', 'go_to_1', "Move to the set absolute value")

        self.add_widget('move2', SpinBox)
        self.get_action('move2').setStyleSheet("background-color : lightcoral; color: black")
        self.add_action('move_abs_2', 'Move Abs', 'go_to_2', "Move to the other set absolute value")

    def connect_things(self):
        self.connect_action('grab', self.modules_manager.get_mod_from_name('Camera').grab)
        self.connect_action('snap', self.modules_manager.get_mod_from_name('Camera').snap)
        self.modules_manager.get_mod_from_name('Camera').grab_done_signal.connect(self.show_data)
        self.connect_action('show', lambda x: self.dashboard.mainwindow.setVisible(x))

        self.connect_action('quit', self.quit)

    def quit(self):
        self.dashboard.quit_fun()
        self.parent.close()

    def setup_docks(self):
        """
        to be subclassed to setup the docks layout
        for instance:

        self.docks['ADock'] = gutils.Dock('ADock name)
        self.dockarea.addDock(self.docks['ADock"])
        self.docks['AnotherDock'] = gutils.Dock('AnotherDock name)
        self.dockarea.addDock(self.docks['AnotherDock"], 'bottom', self.docks['ADock"])

        See Also
        ########
        pyqtgraph.dockarea.Dock
        """
        self.docks['viewer2D'] = gutils.Dock('Viewers')
        self.dockarea.addDock(self.docks['viewer2D'])

        widg1 = QtWidgets.QWidget()
        self.viewer2D = Viewer2D(widg1)
        self.docks['viewer2D'].addWidget(widg1)

    def setup_menu(self):
        '''
        to be subclassed
        create menu for actions contained into the self.actions_manager, for instance:

        For instance:

        file_menu = self.menubar.addMenu('File')
        self.actions_manager.affect_to('load', file_menu)
        self.actions_manager.affect_to('save', file_menu)

        file_menu.addSeparator()
        self.actions_manager.affect_to('quit', file_menu)
        '''
        pass

    def value_changed(self, param):
        ''' to be subclassed for actions to perform when one of the param's value in self.settings is changed

        For instance:
        if param.name() == 'do_something':
            if param.value():
                print('Do something')
                self.settings.child('main_settings', 'something_done').setValue(False)

        Parameters
        ----------
        param: (Parameter) the parameter whose value just changed
        '''
        if param.name() == 'do_something':
            if param.value():
                self.modules_manager.det_done_signal.connect(self.show_data)
            else:
                self.modules_manager.det_done_signal.disconnect()

    def param_deleted(self, param):
        ''' to be subclassed for actions to perform when one of the param in self.settings has been deleted

        Parameters
        ----------
        param: (Parameter) the parameter that has been deleted
        '''
        raise NotImplementedError

    def child_added(self, param):
        ''' to be subclassed for actions to perform when a param  has been added in self.settings

        Parameters
        ----------
        param: (Parameter) the parameter that has been deleted
        '''
        raise NotImplementedError


    def show_data(self, dte: DataToExport):

        dwa = dte.get_data_from_dim('Data2D')[0]

        self.viewer2D.show_data(dwa)


def main():
    import sys
    from pymodaq.dashboard import DashBoard
    from pathlib import Path
    app = QtWidgets.QApplication(sys.argv)
    if config['style']['darkstyle']:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet())

    from pymodaq.dashboard import DashBoard, extensions

    ext = utils.find_dict_in_list_from_key_val(extensions, 'name', EXTENSION_NAME)
    win = QtWidgets.QMainWindow()
    area = gutils.dock.DockArea()
    win.setCentralWidget(area)
    win.resize(1000, 500)
    win.setWindowTitle('PyMoDAQ Dashboard')

    dashboard = DashBoard(area)


    file = Path("../resources/FTIR_JM.xml")
    if file.exists():
        dashboard.set_preset_mode(file)
        prog = dashboard.load_extensions_module(ext)
    else:
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(f"The default file specified in the configuration file does not exists!\n"
                       f"{file}\n"
                       f"Impossible to load the DAQ_Scan Module")
        msgBox.setStandardButtons(msgBox.Ok)
        ret = msgBox.exec()

    win.hide()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


