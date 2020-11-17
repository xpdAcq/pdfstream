"""The analysis server. Process raw image to PDF."""
import typing as tp

import databroker
from bluesky.callbacks.zmq import RemoteDispatcher
from databroker.v2 import Broker
from event_model import RunRouter
from ophyd.sim import NumpySeqHandler

from pdfstream.callbacks.basic import StartStopCallback
from pdfstream.vend.qt_kicker import install_qt_kicker
from .config import ServerConfig
from .tools import run_server
from ..callbacks.analysis import AnalysisConfig, VisConfig, ExportConfig, AnalysisStream, Exporter, Visualizer
from ..callbacks.calibration import CalibrationConfig, Calibration


class XPDConfig(AnalysisConfig, VisConfig, ExportConfig, CalibrationConfig):
    """The configuration for the xpd data reduction. It consists of analysis, visualization and exportation."""

    def __init__(self, *args, **kwargs):
        super(XPDConfig, self).__init__(*args, **kwargs)
        self._an_db = None

    @property
    def an_db(self) -> tp.Union[None, Broker]:
        name = self.get("DATABASE", "an_db", fallback=None)
        if name:
            self._an_db = databroker.catalog[name]
        return self._an_db

    @an_db.setter
    def an_db(self, db: Broker):
        self._an_db = db


class XPDServerConfig(XPDConfig, ServerConfig):
    """The configuration for xpd server."""
    pass


class XPDServer(RemoteDispatcher):
    """The server of XPD data analysis. It is a live dispatcher with XPDRouter subscribed."""

    def __init__(self, config: XPDServerConfig):
        super(XPDServer, self).__init__(config.address, prefix=config.prefix)
        self.subscribe(XPDRouter(config))
        self.subscribe(StartStopCallback())
        install_qt_kicker(self.loop)


def make_and_run(
    cfg_file: str = "~/.config/acq/xpd_server.ini",
    *,
    suppress_warning: bool = True
):
    """Run the xpd data reduction server.

    The server will receive message from proxy and process the data in the message. The processed data will be
    visualized and exported to database and the file system.

    Parameters
    ----------
    cfg_file :
        The path to configuration .ini file. The default path is "~/.config/acq/xpd_server.ini".

    suppress_warning :
        If True, all warning will be suppressed. Turn it to False when running in a test.
    """
    if suppress_warning:
        import warnings
        warnings.simplefilter("ignore")
    config = XPDServerConfig()
    config.read(cfg_file)
    server = XPDServer(config)
    run_server(server)


class XPDRouter(RunRouter):
    """A router that contains the callbacks for the xpd data reduction."""

    def __init__(self, config: XPDConfig):
        factory = XPDFactory(config)
        super(XPDRouter, self).__init__(
            [factory],
            handler_registry={"NPY_SEQ": NumpySeqHandler}
        )


class XPDFactory:
    """The factory to generate callback for xpd data reduction."""

    def __init__(self, config: XPDConfig):
        self.config = config
        self.analysis = AnalysisStream(config)
        an_db = self.config.an_db
        if an_db is not None:
            self.analysis.subscribe(an_db.v1.insert)
        self.analysis.subscribe(Exporter(config))
        self.analysis.subscribe(Visualizer(config))
        self.calibration = Calibration(config)

    def __call__(self, name: str, doc: dict) -> tp.Tuple[list, list]:
        if name == "start":
            if doc.get(self.config.dark_identifier):
                # dark frame run
                return [], []
            elif doc.get(self.config.calib_identifier):
                # calibration run
                return [self.calibration], []
            else:
                # light frame run
                return [self.analysis], []
        return [], []
