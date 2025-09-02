from .metainfo.metainfo import MetaInfo

__version__ = "0.1.0"
__all__ = ["meta"]

class _MetaProxy(MetaInfo):
    _instance = None
    def __getattr__(self, name):
        if self._instance is None:
            raise RuntimeError("pytest_meta.meta not initialized yet")
        return getattr(self._instance, name)

    def __bool__(self):
        return self._instance is not None

meta = _MetaProxy()