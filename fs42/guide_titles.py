import os
import re


_EPISODE_RE = re.compile(r"(?:^|[\s._-])(?:s\d+[\s._-]*e\d+|\d+x\d+)(?:[\s._-]|$)", re.IGNORECASE)
_SEASON_DIR_RE = re.compile(r"^(?:season[\s._-]*\d+|s\d+)$", re.IGNORECASE)
_INTERNAL_TAGS = {":autobump:", "brb", "content", "off_air", "sign_off"}


def _humanize_label(value):
    if not isinstance(value, str):
        return None
    value = re.sub(r"\s+", " ", value.replace("_", " ")).strip()
    return value or None


def _last_meaningful_path_part(value):
    if not isinstance(value, str):
        return None
    parts = [part.strip() for part in value.replace("\\", "/").split("/") if part.strip()]
    for part in reversed(parts):
        if not _SEASON_DIR_RE.match(part):
            return _humanize_label(part)
    return None


def _looks_like_episode(block, meta):
    if meta and meta.get("type") == "episode":
        return True
    if getattr(block, "sequence_key", None):
        return True

    content = getattr(block, "content", None)
    if content is None or isinstance(content, list):
        return False
    path = getattr(content, "path", "") or ""
    normalized_path = path.replace("\\", "/")
    if _EPISODE_RE.search(os.path.basename(normalized_path)):
        return True
    return any(_SEASON_DIR_RE.match(part) for part in normalized_path.split("/")[:-1])


def _folder_show_title(block):
    content = getattr(block, "content", None)
    if content is None or isinstance(content, list):
        return None
    path = getattr(content, "path", None)
    if not path:
        return None
    normalized_path = path.replace("\\", "/")
    parent, separator, _ = normalized_path.rpartition("/")
    if not separator:
        return None
    return _last_meaningful_path_part(parent)


def guide_titles(block, episode_fallback=None):
    """Return distinct show and episode labels without changing the legacy title."""
    meta = getattr(block, "meta", None)
    if not isinstance(meta, dict):
        meta = {}

    show_title = _humanize_label(meta.get("show_title"))
    is_episode = _looks_like_episode(block, meta)

    content = getattr(block, "content", None)
    if not show_title and is_episode and content is not None and not isinstance(content, list):
        tag = getattr(content, "tag", None)
        if isinstance(tag, str) and tag.casefold() not in _INTERNAL_TAGS:
            show_title = _last_meaningful_path_part(tag)

    if not show_title and is_episode:
        sequence_key = getattr(block, "sequence_key", None)
        if isinstance(sequence_key, dict):
            show_title = _last_meaningful_path_part(sequence_key.get("tag_path"))

    if not show_title and is_episode:
        show_title = _folder_show_title(block)

    episode_title = None
    if meta.get("type") == "episode":
        episode_title = _humanize_label(meta.get("title"))

    if episode_fallback is None:
        episode_fallback = getattr(block, "title", None)
    legacy_title = _humanize_label(episode_fallback)
    if not episode_title and show_title and legacy_title:
        episode_title = legacy_title

    if show_title and episode_title and show_title.casefold() == episode_title.casefold():
        episode_title = None

    return show_title, episode_title
