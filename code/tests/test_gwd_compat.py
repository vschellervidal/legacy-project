from __future__ import annotations

from geneweb.adapters.http.app import _compat_build_gwd_url


def test_compat_build_gwd_url_home() -> None:
    url = _compat_build_gwd_url("/tmp/gwb_test", "", use_python=True)
    assert url.startswith("/gwd?")
    assert "base=%2Ftmp%2Fgwb_test" in url
    assert "use_python=true" in url
    assert "mode=" not in url


def test_compat_build_gwd_url_family() -> None:
    url = _compat_build_gwd_url("/tmp/gwb_test", "F", f="F001")
    assert "mode=F" in url and "f=F001" in url


def test_compat_build_gwd_url_search() -> None:
    url = _compat_build_gwd_url("/tmp/gwb_test", "NG", v="DUPONT")
    assert "mode=NG" in url and "v=DUPONT" in url


def test_compat_build_gwd_url_asc_desc() -> None:
    url_a = _compat_build_gwd_url("/tmp/gwb_test", "A", i="I003")
    url_d = _compat_build_gwd_url("/tmp/gwb_test", "D", i="I001")
    assert "mode=A" in url_a and "i=I003" in url_a
    assert "mode=D" in url_d and "i=I001" in url_d


