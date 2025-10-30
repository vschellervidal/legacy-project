from __future__ import annotations

from pathlib import Path

from geneweb.services.gwd_wiznotes import list_wiznotes, set_wiznote, get_wiznote, del_wiznote


def test_wiznotes_crud(tmp_path: Path) -> None:
    # list vide
    res = list_wiznotes(tmp_path)
    assert res == {"notes": {}}

    # set
    set_wiznote(tmp_path, "IND:I1", "Note A")
    set_wiznote(tmp_path, "FAM:F1", "Note B")

    # get
    n = get_wiznote(tmp_path, "IND:I1")
    assert n["note"] == "Note A"

    # search
    res = list_wiznotes(tmp_path, query="note")
    assert "IND:I1" in res["notes"] and "FAM:F1" in res["notes"]

    # delete
    del_wiznote(tmp_path, "FAM:F1")
    res = list_wiznotes(tmp_path)
    assert "FAM:F1" not in res["notes"]


