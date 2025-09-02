from typing import Optional
from .metainfo.metainfo import MetaInfo

__version__ = "0.1.0"
__all__ = ["meta", "get_meta", "_set_meta"]

# Will be initialized later by the plugin
meta: Optional[MetaInfo] = None

def get_meta() -> MetaInfo:
    """Return the global MetaInfo instance.
    Raises if accessed before pytest has initialized it.
    """
    if meta is None:
        raise RuntimeError(
            "pytest_meta.meta accessed before pytest has created it. "
            "Did you import it too early?"
        )
    return meta

def _set_meta(meta_instance: MetaInfo) -> None:
    """Internal function used by the pytest plugin to set the global instance."""
    global meta
    meta = meta_instance