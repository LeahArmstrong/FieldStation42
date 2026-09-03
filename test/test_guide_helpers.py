import json
import pathlib
import shutil
import subprocess

import pytest


HELPERS = pathlib.Path(__file__).parents[1] / "fs42/fs42_server/static/guide_helpers.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required for browser helper tests")
def test_browser_guide_time_helper():
    script = f"""
const helpers = require({json.dumps(str(HELPERS))});
const at = (hour, minute = 5, second = 9) => new Date(2026, 8, 3, hour, minute, second);
const actual = {{
  midnight: helpers.formatTime(at(0), '%-I:%M %p'),
  noon: helpers.formatTime(at(12), '%I:%M %P'),
  afternoon: helpers.formatTime(at(16), '%H:%M:%S'),
  spacePadded: helpers.formatTime(at(4), '%_H:%_M:%_S'),
  unpadded: helpers.formatTime(at(4), '%-H:%-M:%-S'),
  aliases: helpers.formatTime(at(16), '%R | %r | %%'),
  unknown: helpers.formatTime(at(16), '%Q %H'),
  fullTitles: helpers.programTitles({{title: 'legacy', show_title: 'Daria', episode_title: 'Esteemsters'}}),
  legacyTitle: helpers.programTitles({{title: 'The Matrix'}}),
  duplicate: helpers.programTitles({{title: 'Daria', show_title: 'Daria', episode_title: 'daria'}})
}};
process.stdout.write(JSON.stringify(actual));
"""
    result = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)

    assert json.loads(result.stdout) == {
        "midnight": "12:05 AM",
        "noon": "12:05 pm",
        "afternoon": "16:05:09",
        "spacePadded": " 4: 5: 9",
        "unpadded": "4:5:9",
        "aliases": "16:05 | 04:05:09 PM | %",
        "unknown": "%Q 16",
        "fullTitles": {"primary": "Daria", "secondary": "Esteemsters"},
        "legacyTitle": {"primary": "The Matrix", "secondary": ""},
        "duplicate": {"primary": "Daria", "secondary": ""},
    }


def test_browser_guides_use_shared_time_helper():
    static_root = HELPERS.parent
    standard_guide = (static_root / "guide_frame.html").read_text()
    custom_guide = (static_root / "customguide/customguide.js").read_text()

    assert "fetchGuideConfig()" in standard_guide
    assert "fetchGuideConfig()" in custom_guide
    assert "formatTime12" not in custom_guide
    assert "hour12:" not in standard_guide
    assert "formatDateForAPI(guideEndTime),\n                        true" in standard_guide
    assert "programTitles(block)" in standard_guide
    assert "programTitles(block)" in custom_guide
    assert "episodeSpan.textContent = episodeTitle" in standard_guide


def test_standard_guide_reloads_its_nested_frame():
    guide_page = (HELPERS.parent / "guide.html").read_text()

    assert "guide_frame.html?v=" in guide_page
    assert "Date.now()" in guide_page
