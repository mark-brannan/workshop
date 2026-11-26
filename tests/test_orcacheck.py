import json, zipfile

from shop import orcacheck

FLOAT = "It seems object OpenSCAD Model has floating regions. Please re-orient the object or enable support generation."


def test_messages_dedupes_plate_and_global_warning():
    r = {"return_code": 0, "error_string": "Success.", "sliced_plates": [{"warning_message": FLOAT}],
         "warnings": [{"text": FLOAT}]}
    assert orcacheck.messages(r) == [FLOAT]


def test_messages_clean_slice_is_silent():
    assert orcacheck.messages({"return_code": 0, "sliced_plates": [{"warning_message": ""}], "warnings": []}) == []


def test_messages_failed_slice_says_so():
    assert orcacheck.messages({"return_code": -51, "error_string": "bad params"}) == ["Orca could not slice it: bad params"]


def test_skips_3mf_without_saved_settings(tmp_path, monkeypatch):
    f = tmp_path / "a.3mf"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("3D/3dmodel.model", "<model/>")
    monkeypatch.setattr(orcacheck.shutil, "which", lambda _: "/bin/true")
    assert not orcacheck.has_settings(f)
    assert orcacheck.warnings(f) == []


def test_reads_orca_result(tmp_path, monkeypatch):
    f = tmp_path / "a.3mf"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr(orcacheck.SETTINGS, "{}")
    monkeypatch.setattr(orcacheck.shutil, "which", lambda _: "orca-slicer")

    def fake_run(cmd, cwd, **_):
        (orcacheck.Path(cwd) / "result.json").write_text(json.dumps({"return_code": 0, "sliced_plates": [{"warning_message": FLOAT}]}))
    monkeypatch.setattr(orcacheck.subprocess, "run", fake_run)
    assert orcacheck.warnings(f) == [f"Orca: {FLOAT}"]
