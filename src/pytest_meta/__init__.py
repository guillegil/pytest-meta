from .metainfo.metainfo import MetaInfo

__all__ = ["meta"]

class _MetaProxy(MetaInfo):
    _instance = None

    def __getattr__(self, name):
        print(f"DEBUG: _MetaProxy.__getattr__ called with name='{name}', _instance={self._instance}")
        if self._instance is None:
            raise RuntimeError("pytest_meta.meta not initialized yet")
        return getattr(self._instance, name)

    def __bool__(self):
        print(f"DEBUG: _MetaProxy.__bool__ called, _instance={self._instance}")
        return self._instance is not None
    
    def __repr__(self):
        return f"<_MetaProxy(_instance={self._instance})>"

print("DEBUG: Creating meta proxy")
meta = _MetaProxy()
print(f"DEBUG: meta created: {meta}")