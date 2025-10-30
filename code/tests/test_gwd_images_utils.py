from __future__ import annotations

from pathlib import Path

from geneweb.services.gwd_images import list_carrousel_images, set_blason_image


def test_list_images(tmp_path: Path) -> None:
    # Crée une image factice
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    (img_dir / "I001_photo.png").write_bytes(b"\x89PNG\r\n")

    res = list_carrousel_images(tmp_path, person_id="I001")
    assert res["images"] and "I001_photo.png" in res["images"][0]


def test_utils_smoke_no_http(tmp_path: Path) -> None:
    # chk_data util (via service I/O direct)
    (tmp_path / "index.json").write_text("[]", encoding="utf-8")
    # blason (service direct)
    res = set_blason_image(tmp_path, "I001", "blason.png")
    assert res["person_id"] == "I001"

