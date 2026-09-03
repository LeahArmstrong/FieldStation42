import datetime
import importlib.util
import pathlib
from types import SimpleNamespace

from fs42.guide_titles import guide_titles


def load_api_module(name):
    path = pathlib.Path(__file__).parents[1] / f"fs42/fs42_server/api/{name}.py"
    spec = importlib.util.spec_from_file_location(f"test_{name}_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schedules = load_api_module("schedules")
_attach_guide_titles = schedules._attach_guide_titles
_listing_projection = schedules._listing_projection


def make_block(
    *,
    title="Episode Title",
    path="/media/Daria/Season 1/Daria S01E01 - Esteemsters.mkv",
    tag="Daria",
    sequence_key=None,
    meta=None,
    content=None,
):
    if content is None:
        content = SimpleNamespace(path=path, tag=tag)
    block = SimpleNamespace(
        title=title,
        content=content,
        sequence_key=sequence_key,
        start_time=datetime.datetime(2026, 9, 3, 16, 30),
        end_time=datetime.datetime(2026, 9, 3, 17, 0),
    )
    if meta is not None:
        block.meta = meta
    return block


def test_nfo_titles_win_over_tag_and_folder_fallbacks():
    block = make_block(
        tag="Wrong Tag",
        meta={"type": "episode", "show_title": "Daria", "title": "Esteemsters"},
    )

    assert guide_titles(block) == ("Daria", "Esteemsters")


def test_scheduled_tag_wins_over_active_child_sequence():
    block = make_block(
        title="Esteemsters",
        tag="Daria",
        sequence_key={"tag_path": "Daria/Season 2"},
    )

    assert guide_titles(block) == ("Daria", "Esteemsters")


def test_folder_fallback_skips_season_directory_for_posix_and_windows_paths():
    posix = make_block(tag="content", path="/media/A Place Further/season_01/S01E01 - Youth.mkv")
    windows = make_block(tag="content", path=r"C:\media\A Place Further\S03\S03E02 - Youth.mkv")

    assert guide_titles(posix) == ("A Place Further", "Episode Title")
    assert guide_titles(windows) == ("A Place Further", "Episode Title")


def test_duplicate_episode_title_is_suppressed():
    block = make_block(title="Daria")

    assert guide_titles(block) == ("Daria", None)


def test_non_episode_and_multi_content_blocks_keep_legacy_title_only():
    movie = make_block(title="The Matrix", path="/media/movies/The Matrix.mkv", tag="movies")
    clip_show = make_block(title="Toonami", content=[SimpleNamespace(path="one.mkv", tag="clips")])
    bare_path = make_block(title="Episode Title", path="S01E01.mkv", tag="content")

    assert guide_titles(movie) == (None, None)
    assert guide_titles(clip_show) == (None, None)
    assert guide_titles(bare_path) == (None, None)


def test_listing_projection_is_additive_and_preserves_optional_meta():
    meta = {"type": "episode", "show_title": "Daria", "title": "Esteemsters"}
    block = make_block(meta=meta)

    without_meta = _listing_projection([block], include_meta=False)[0]
    with_meta = _listing_projection([block], include_meta=True)[0]

    assert without_meta == {
        "title": "Episode Title",
        "show_title": "Daria",
        "episode_title": "Esteemsters",
        "start_time": "2026-09-03T16:30:00",
        "end_time": "2026-09-03T17:00:00",
    }
    assert with_meta == {**without_meta, "meta": meta}


def test_full_schedule_blocks_receive_display_fields():
    block = make_block(title="Esteemsters")

    assert _attach_guide_titles([block]) == [block]
    assert block.show_title == "Daria"
    assert block.episode_title == "Esteemsters"
