from .metainfo.metainfo import MetaInfo

__version__ = "0.1.0"
__all__ = ["meta", "get_meta", "_set_meta"]

# Will be initialized later by the plugin
meta: MetaInfo = None
