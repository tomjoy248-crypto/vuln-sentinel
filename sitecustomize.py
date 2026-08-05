import builtins
from pathlib import Path


_real_open = builtins.open


def _utf8_open(file, mode="r", *args, **kwargs):
    if "b" in mode:
        return _real_open(file, mode, *args, **kwargs)
    if "encoding" not in kwargs:
        kwargs["encoding"] = "utf-8"
    if "errors" not in kwargs:
        kwargs["errors"] = "strict"
    return _real_open(file, mode, *args, **kwargs)


builtins.open = _utf8_open


_original_path_open = Path.open


def _path_open(self, mode="r", *args, **kwargs):
    if "b" in mode:
        return _original_path_open(self, mode, *args, **kwargs)
    if "encoding" not in kwargs:
        kwargs["encoding"] = "utf-8"
    if "errors" not in kwargs:
        kwargs["errors"] = "strict"
    return _original_path_open(self, mode, *args, **kwargs)


Path.open = _path_open
