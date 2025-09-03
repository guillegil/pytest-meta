
from .metainfo.metainfo import MetaInfo

meta : MetaInfo = None

def _set_meta(new_meta : MetaInfo):
    global meta
    meta = new_meta

__all__ = ['meta']