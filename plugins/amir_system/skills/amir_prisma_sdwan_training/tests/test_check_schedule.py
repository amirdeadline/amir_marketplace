"""Tests for scripts/check_schedule.py. Run: python -m pytest -q -p no:cacheprovider tests"""
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import check_schedule as cs  # noqa: E402

DAY = """## Day {n} — title
| Start | End | Type | Session |
|---|---|---|---|
| 09:00 | 10:30 | Theory | A |
| 10:30 | 10:45 | Break | coffee |
| 10:45 | 12:30 | Lab | B |
| 12:30 | 13:00 | Lunch | lunch |
| 13:00 | 15:00 | Theory | C |
| 15:00 | 15:15 | Break | tea |
| 15:15 | 17:00 | Lab | D |
"""


def _plan(days):
    return "# Plan\n" + "\n".join(DAY.format(n=i + 1) for i in range(days))


def test_basic_passes_for_five_eight_hour_days(tmp_path, capsys):
    p = tmp_path / "plan.md"
    p.write_text(_plan(5), encoding="utf-8")
    assert cs.check_basic(p, 5, 8.0) == 0
    out = capsys.readouterr().out
    assert "Total scheduled 40.00 h" in out and "contact 35.00 h" in out and "breaks 5.00 h" in out


def test_basic_fails_on_wrong_day_count_and_gap(tmp_path, capsys):
    p = tmp_path / "plan.md"
    text = _plan(4) + "## Day 5\n| Start | End | Type |\n|---|---|---|\n| 09:00 | 12:00 | Theory |\n| 13:00 | 18:00 | Lab |\n"
    p.write_text(text, encoding="utf-8")
    assert cs.check_basic(p, 5, 8.0) == 1
    out = capsys.readouterr().out
    assert "gap/overlap" in out


def test_basic_missing_tables_returns_2(tmp_path):
    p = tmp_path / "plan.md"
    p.write_text("# nothing here\n", encoding="utf-8")
    assert cs.check_basic(p, 5, 8.0) == 2


ADV = """## Modules
| ID | Module | Theory h | Demo h | Lab h | Assessment h | Total h |
|---|---|---|---|---|---|---|
| A1 | Design | 3 | 1 | 2 | 0.5 | 6.5 |
| A2 | Routing | 2 | 1 | 4 | 1 | 8 |
| Total | | 5 | 2 | 6 | 1.5 | 14.5 |
"""


def test_advanced_passes(tmp_path):
    p = tmp_path / "adv.md"
    p.write_text(ADV, encoding="utf-8")
    assert cs.check_advanced(p) == 0


def test_advanced_detects_bad_row_and_total(tmp_path, capsys):
    p = tmp_path / "adv.md"
    p.write_text(ADV.replace("| 8 |", "| 9 |"), encoding="utf-8")
    assert cs.check_advanced(p) == 1
    assert "FAIL A2" in capsys.readouterr().out


def test_main_dispatch(tmp_path):
    p = tmp_path / "adv.md"
    p.write_text(ADV, encoding="utf-8")
    assert cs.main(["advanced", str(p)]) == 0
    assert cs.main(["basic", str(tmp_path / "missing.md")]) == 2
