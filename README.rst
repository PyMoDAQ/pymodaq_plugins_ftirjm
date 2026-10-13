pymodaq_plugins_ftirjm
######################

.. image:: https://img.shields.io/pypi/v/pymodaq_plugins_ftirjm.svg
   :target: https://pypi.org/project/pymodaq_plugins_ftirjm/
   :alt: Latest Version

.. image:: https://readthedocs.org/projects/pymodaq/badge/?version=latest
   :target: https://pymodaq.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status

.. image:: https://github.com/PyMoDAQ/pymodaq_plugins_ftirjm/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/PyMoDAQ/pymodaq_plugins_ftirjm/actions/workflows/tests.yml

Specific PyMoDAQ extension for JM Poumirol's FTIR at CEMES lab, meant to be driven from a Raspberry Pi touch screen.
Targets **PyMoDAQ 5.3.x** (Python 3.10 to 3.13).


Authors
=======

* Sebastien Weber  (sebastien.weber@cnrs.fr)


Extensions
==========

* **FTIR_JM**: shows the images of a camera and moves an Elliptec rotator between two configurable positions.

The instruments come from the Dashboard's experiment: an actuator named ``Elliptec`` and a 2D detector named
``Camera`` (names and positions are in the ``config_ftirjm.toml`` configuration file). The instrument plugins come
from other packages, installed as dependencies:

* the Elliptec actuator of `pymodaq_plugins_thorlabs <https://github.com/PyMoDAQ/pymodaq_plugins_thorlabs>`_
* the PiCamera detector of `pymodaq_plugins_raspberry <https://github.com/PyMoDAQ/pymodaq_plugins_raspberry>`_
  (installed on a Raspberry Pi only: ``aarch64`` or ``armv7l``)

Two experiments are shipped in ``resources`` and copied in PyMoDAQ's experiment folder when the extension is run
on its own:

* ``FTIR_JM``: Elliptec and PiCamera
* ``FTIR_JM_mock``: the same with the Mock plugins, to try the extension without hardware

Run it with ``python -m pymodaq_plugins_ftirjm.extensions.ftirjm`` (loads ``FTIR_JM``), or
``python -m pymodaq_plugins_ftirjm.extensions.ftirjm -x FTIR_JM_mock``. It is also listed in the Dashboard's
extension menu.
