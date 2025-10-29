from __future__ import annotations

from geneweb.services.comparator import compare_gedcom, normalize_gedcom


def test_normalize_gedcom_basic() -> None:
    a = """
    0 HEAD
    1  CHAR   UTF-8

    0 @I1@  INDI
    1 NAME Jean /DUPONT/
    """
    lines = normalize_gedcom(a)
    assert lines[0] == "0 HEAD"
    assert lines[1] == "1 CHAR UTF-8"
    assert lines[2] == "0 @I1@ INDI"
    assert lines[3] == "1 NAME Jean /DUPONT/"


def test_compare_equal_after_normalization() -> None:
    left = """
    0 HEAD
    1 CHAR UTF-8
    0 @I1@ INDI
    1 NAME Jean /DUPONT/
    0 TRLR
    """
    right = """
    0  HEAD
      1   CHAR  UTF-8
    0   @I1@   INDI
    1  NAME  Jean   /DUPONT/

    0 TRLR
    """
    res = compare_gedcom(left, right)
    assert res.are_equal is True
    assert res.diff == ""


def test_compare_diff_detects_difference() -> None:
    left = """
    0 HEAD
    1 CHAR UTF-8
    0 @I1@ INDI
    1 NAME Jean /DUPONT/
    0 TRLR
    """
    right = """
    0 HEAD
    1 CHAR UTF-8
    0 @I1@ INDI
    1 NAME Jean /MARTIN/
    0 TRLR
    """
    res = compare_gedcom(left, right)
    assert res.are_equal is False
    assert "-1 NAME Jean /DUPONT/" in res.diff
    assert "+1 NAME Jean /MARTIN/" in res.diff


