import datetime
import pathlib
from types import SimpleNamespace
from unittest.mock import patch

from fs42 import guide_builder


def long_episode(title="Fire!"):
    start = datetime.datetime(2026, 9, 3, 17, 30, 1)
    return SimpleNamespace(
        title=title,
        content=SimpleNamespace(
            path="/media/Daria/Season 2/Daria S02E13 - Write Where It Hurts.mkv",
            tag="Daria",
        ),
        sequence_key={"tag_path": "Daria"},
        start_time=start,
        end_time=start + datetime.timedelta(hours=2),
        playback_duration=lambda: 7200,
    )


def test_preview_block_formats_native_show_and_episode_lines():
    preview = guide_builder.PreviewBlock(
        "Fire!", show_title="Daria", episode_title="Fire!"
    )

    assert preview.title == "Fire!"
    assert preview.display_title == "Daria\nFire!"
    assert guide_builder.PreviewBlock("Fire!").display_title == "Fire!"
    assert guide_builder.PreviewBlock(
        "Daria", show_title="Daria", episode_title="daria"
    ).display_title == "Daria"

    native_guide = (
        pathlib.Path(__file__).parents[1] / "fs42/guide_tk.py"
    ).read_text()
    assert "text=c.display_title" in native_guide


def test_native_schedule_preview_infers_show_and_episode_titles():
    block = long_episode()
    manager = SimpleNamespace(get_programming_block=lambda *_: block)

    with patch.object(guide_builder, "LiquidManager", return_value=manager):
        preview = guide_builder.ScheduleQuery.query_slot(
            "MTV", block.start_time, normalize=False
        )[0]

    assert preview.title == "Fire!"
    assert preview.show_title == "Daria"
    assert preview.episode_title == "Fire!"
    assert preview.display_title == "Daria\nFire!"


def test_native_schedule_preview_uses_normalized_episode_title():
    block = long_episode("Daria S02E13 - Write Where It Hurts - restored")
    manager = SimpleNamespace(get_programming_block=lambda *_: block)

    with (
        patch.object(guide_builder, "LiquidManager", return_value=manager),
        patch.object(guide_builder, "normalize_video_title", return_value="Write Where It Hurts"),
    ):
        preview = guide_builder.ScheduleQuery.query_slot(
            "MTV", block.start_time, normalize=True
        )[0]

    assert preview.title == "Write Where It Hurts"
    assert preview.show_title == "Daria"
    assert preview.episode_title == "Write Where It Hurts"
    assert preview.display_title == "Daria\nWrite Where It Hurts"
