from .metainfo.metainfo import MetaInfo

__version__ = "0.1.0"
__all__ = ["meta"]

# This will be the global instance that gets exposed
meta = None

def get_meta() -> MetaInfo:
    """Get the current meta instance."""
    return meta

def _set_meta(meta_instance: MetaInfo):
    """Internal function to set the meta instance."""
    global meta
    meta = meta_instance