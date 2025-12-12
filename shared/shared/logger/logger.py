import logging

from shared.config.logger import LoggerConfig

try:
    from pythonjsonlogger import jsonlogger  # type: ignore
    HAS_JSONLOGGER = True
except ImportError:
    HAS_JSONLOGGER = False
try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


def set_logger(cfg: LoggerConfig):
    root = logging.getLogger()
    root.setLevel(cfg.level)

    if cfg.filename:
        handler = logging.FileHandler(cfg.filename)
    else:
        handler = logging.StreamHandler()
    
    if HAS_JSONLOGGER and cfg.formatter == "json":
        from pythonjsonlogger.json import JsonFormatter
        formatter = JsonFormatter(fmt=cfg.fmt) if cfg.fmt else JsonFormatter()
    elif HAS_JSONLOGGER and HAS_ORJSON and cfg.formatter == "orjson":
        from pythonjsonlogger.orjson import OrjsonFormatter
        formatter = OrjsonFormatter(fmt=cfg.fmt) if cfg.fmt else OrjsonFormatter()
    else:
        formatter = logging.Formatter(fmt=cfg.fmt) if cfg.fmt else logging.Formatter()
    
    handler.setFormatter(formatter)
    root.addHandler(handler)

def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)