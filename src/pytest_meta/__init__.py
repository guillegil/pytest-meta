from .metainfo.metainfo import MetaInfo

class _MetaProxy(MetaInfo):
    _instance: MetaInfo | None = None

    @classmethod
    def set(cls, tool: MetaInfo) -> None:
        cls._instance = tool

    def __getattr__(self, name):
        """Forward attribute access to the real MyTool instance."""
        if self._instance is None:
            raise RuntimeError("mytool is not initialized yet")
        return getattr(self._instance, name)

    def __call__(self, *args, **kwargs):
        """Optionally forward call if MyTool is callable."""
        if self._instance is None:
            raise RuntimeError("mytool is not initialized yet")
        return self._instance(*args, **kwargs)

# exported proxy
meta : MetaInfo = _MetaProxy()

__all__ = ["meta"]