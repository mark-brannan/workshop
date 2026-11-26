from shop.printwatch import MACROS, PATCHES, Job, Soak, job_checks

ASA = Job("box.gcode", "ASA-CF", 90.0, 102.4)
GOOD_PATCHES = {name: 1 for name in PATCHES}


def state(z=20.0, homed="xyz", box=0, job="complete", web="ready", bed=(21.0, 0.0), chamber=(13.0, 0.0)):
    return {
        "webhooks": {"state": web, "state_message": "Heater heater_bed not heating at expected rate"},
        "print_stats": {"state": job},
        "toolhead": {"position": [225.0, 345.0, z, 0.0], "homed_axes": homed},
        "heater_bed": {"temperature": bed[0], "target": bed[1]},
        "heater_generic chamber_heater": {"target": chamber[1]},
        "temperature_sensor chamber_temp": {"temperature": chamber[0]},
        "box": {"enable": box},
    }


def failed(st, job=ASA, plate="frosted", vents="closed", cfs=False, macros=set(MACROS), patches=GOOD_PATCHES):
    return [c for c in job_checks(st, job, plate, vents, cfs, macros, patches) if c.level == "FAIL"]


def test_clean_spool_asa_job_passes():
    assert failed(state()) == []


def test_low_homed_z_fails_with_a_lift_fix():
    # 2026-11-22: a job started at Z -1.67 homed XY with the nozzle in the plate.
    (f,) = failed(state(z=-1.67))
    assert "G1 Z10" in f.fix


def test_unhomed_z_warns_but_does_not_fail():
    assert failed(state(z=-1.67, homed="")) == []


def test_asa_on_the_80c_pattern_plate_fails():
    assert len(failed(state(), plate="pattern")) == 1


def test_petg_on_pattern_plate_with_open_vents_passes():
    assert failed(state(), job=Job("p.gcode", "PETG", 70.0, 10.0), plate="pattern", vents="open") == []


def test_open_vents_fail_a_high_temp_job():
    assert len(failed(state(), vents="open")) == 1


def test_spool_job_with_cfs_on_fails_with_cfs_off_fix():
    (f,) = failed(state(box=1))
    assert "BOX_ENABLE_CFS_PRINT ENABLE=0" in f.fix


def test_spool_job_with_a_tool_change_in_the_file_fails():
    job = Job("box.gcode", "ASA-CF", 90.0, 102.4, ["line 40 T0"])
    assert len(failed(state(), job=job)) == 1


def test_busy_printer_fails():
    assert len(failed(state(job="printing"))) == 1


def test_firmware_update_casualties_fail():
    lost = {**GOOD_PATCHES, next(iter(PATCHES)): 0}
    assert len(failed(state(), macros={"BED_VIEW"}, patches=lost)) == 2


def test_unreadable_patches_warn_only():
    assert failed(state(), patches=None) == []


def soaking(bed_t, ch_t=40.0):
    return state(bed=(bed_t, 90.0), chamber=(ch_t, 50.0))


def test_soak_passes_after_45_minutes_at_target_and_warm_chamber():
    s = Soak(bed=90, chamber=50, deadline_s=110 * 60)
    assert s.update(0, soaking(60)) == ""
    assert s.update(30 * 60, soaking(89)) == ""
    assert s.update(74 * 60, soaking(90)) == ""
    assert s.update(75 * 60, soaking(90)) == "PASS"


def test_soak_clock_restarts_when_the_bed_drops_out_of_band():
    s = Soak(bed=90, chamber=50, deadline_s=200 * 60)
    s.update(0, soaking(90))
    s.update(40 * 60, soaking(80))
    assert s.update(60 * 60, soaking(90)) == ""
    assert s.held_min(60 * 60) == 0


def test_soak_waits_on_a_cold_chamber():
    s = Soak(bed=90, chamber=50, deadline_s=200 * 60)
    s.update(0, soaking(90, ch_t=25))
    assert s.update(50 * 60, soaking(90, ch_t=25)) == ""


def test_soak_fails_when_the_hold_ends():
    s = Soak(bed=90, chamber=50, deadline_s=110 * 60)
    assert s.update(60, state(bed=(90, 0.0), chamber=(40, 0.0))).startswith("FAIL")


def test_soak_fails_on_a_heater_fault():
    s = Soak(bed=90, chamber=50, deadline_s=110 * 60)
    assert "not heating" in s.update(60, {**soaking(50), "webhooks": {"state": "shutdown", "state_message": "Heater heater_bed not heating at expected rate"}})


def test_soak_fails_at_the_deadline():
    s = Soak(bed=90, chamber=50, deadline_s=110 * 60)
    assert s.update(110 * 60, soaking(70)).startswith("FAIL: not soaked")


def run_start(monkeypatch, preflight_rc=0, box_after=0, cfs=False):
    import argparse

    from shop import printwatch as pw

    sent = []
    monkeypatch.setattr(pw, "preflight", lambda a, fix=None: preflight_rc)
    monkeypatch.setattr(pw, "gcode", lambda s: sent.append(s))
    monkeypatch.setattr(pw.time, "sleep", lambda s: None)
    monkeypatch.setattr(pw, "api", lambda path, body=None, timeout=5: sent.append(path) or {})
    monkeypatch.setattr(pw, "fetch", lambda objs: {"box": {"enable": box_after}, "print_stats": {"state": "printing", "filename": "box.gcode"}})
    a = argparse.Namespace(file="box.gcode", plate="frosted", vents="closed", cfs=cfs, fix=False)
    return pw.start(a), sent


def test_start_resends_cfs_off_then_starts_the_file(monkeypatch):
    rc, sent = run_start(monkeypatch)
    assert rc == 0
    assert sent[0].startswith("BOX_ENABLE_CFS_PRINT ENABLE=0")
    assert sent[1] == "/printer/print/start?filename=box.gcode"


def test_start_refuses_on_a_failed_preflight(monkeypatch):
    rc, sent = run_start(monkeypatch, preflight_rc=1)
    assert rc == 1 and sent == []


def test_start_refuses_when_the_screen_holds_cfs_on(monkeypatch):
    rc, sent = run_start(monkeypatch, box_after=1)
    assert rc == 1 and not any("print/start" in s for s in sent)


def test_soak_refuses_a_bed_over_the_plate_rating(monkeypatch):
    import argparse

    from shop import printwatch as pw

    sent = []
    monkeypatch.setattr(pw, "fetch", lambda objs: state())
    monkeypatch.setattr(pw, "gcode", lambda s: sent.append(s))
    a = argparse.Namespace(file="box.gcode", bed=90.0, plate="pattern", over_rating=False)
    assert pw.soak(a) == 1 and sent == []


from shop.printwatch import checkpoint_due, fault_keys, recoverable, taper_pct  # noqa: E402


def test_first_checkpoint_waits_for_layer_2s_frame():
    assert checkpoint_due(2, set()) is None
    assert checkpoint_due(3, set()) == 2


def test_checkpoints_run_2_10_50_then_every_100():
    seen, got = set(), []
    for layer in range(1, 330):
        c = checkpoint_due(layer, seen)
        if c is not None:
            seen.add(c)
            got.append(c)
    assert got == [2, 10, 50, 100, 200, 300]


def test_a_late_start_takes_only_the_newest_checkpoint():
    assert checkpoint_due(237, set()) == 200
    assert checkpoint_due(237, {200}) is None


def test_taper_is_flat_below_60_and_70_percent_at_the_top():
    assert taper_pct(40, 102.4) == 100
    assert taper_pct(60, 102.4) == 100
    assert taper_pct(102.4, 102.4) == 70
    assert taper_pct(81.2, 102.4) == 85


def test_no_taper_on_a_short_part():
    assert taper_pct(5, 5.6) == 100


def test_fault_keys_read_messages_and_only_new_console_lines():
    st = {"webhooks": {"state_message": "Printer is ready"}, "print_stats": {"message": ""}}
    store = [{"message": '!! {"code":"key22","msg":"No trigger on y"}', "time": 100.0}, {"message": "key852 retrude_err", "time": 200.0}]
    assert fault_keys(st, store, 150.0) == ["key852"]


def test_recovery_only_known_faults_before_layer_1_and_at_most_twice():
    assert recoverable(["key22"], 0, 0)
    assert not recoverable(["key22"], 1, 0)  # never mid-print
    assert not recoverable(["key836"], 0, 0)  # unknown fault: the user's call
    assert not recoverable(["key22"], 0, 2)
    assert not recoverable([], 0, 0)


def watch_args(**kw):
    import argparse

    base = dict(file=None, plate=None, vents=None, cfs=False, frames=None, taper=False, taper_from=60, taper_to=70, poll=0, stall_min=20)
    return argparse.Namespace(**{**base, **kw})


def fake_printer(monkeypatch, tmp_path, state, filename):
    from shop import printwatch as pw

    st = {"webhooks": {"state": "ready"}, "print_stats": {"state": state, "filename": filename, "info": {"current_layer": 3}},
          "virtual_sdcard": {"file_position": 1}, "gcode_move": {}}
    monkeypatch.setattr(pw, "fetch", lambda objs: st)
    monkeypatch.setattr(pw, "api", lambda path, body=None, timeout=5: {"gcode_store": []})
    monkeypatch.setattr(pw, "read_job", lambda name: Job(name, "ASA", 90, 50, []))
    monkeypatch.setattr(pw.Path, "home", lambda: tmp_path)
    return pw


def test_next_watches_the_printing_job(monkeypatch, tmp_path, capsys):
    pw = fake_printer(monkeypatch, tmp_path, "printing", "lid.gcode")
    monkeypatch.setattr(pw, "frame", lambda a: 0)
    a = watch_args()
    assert pw.next_(a) == 0
    assert a.file == "lid.gcode"
    assert "CHECKPOINT" in capsys.readouterr().out


def test_next_with_no_job_printing_refuses(monkeypatch, tmp_path, capsys):
    pw = fake_printer(monkeypatch, tmp_path, "standby", "")
    assert pw.next_(watch_args()) == 1
    assert "no job is printing" in capsys.readouterr().out


def test_next_takes_no_file_argument():
    import pytest

    from shop import printwatch as pw

    with pytest.raises(SystemExit):
        pw.main(["next", "lid.gcode"])


def test_start_carries_on_when_the_start_request_times_out(monkeypatch):
    # 2026-11-23: Moonraker held the start reply past 5 s while the job's start mesh ran.
    from shop import printwatch as pw

    def slow(path, body=None, timeout=5):
        raise TimeoutError

    rc, sent = run_start(monkeypatch)
    monkeypatch.setattr(pw, "api", slow)
    a = __import__("argparse").Namespace(file="box.gcode", plate="frosted", vents="closed", cfs=False, fix=False)
    assert pw.start(a) == 0


def test_a_spool_upload_drops_only_tool_change_lines():
    from shop.printwatch import spool_gcode

    src = b"START_PRINT EXTRUDER_TEMP=250\nT0\nM109 S250\n;T0 in a comment\nTIMELAPSE_TAKE_FRAME\nT12\n"
    assert spool_gcode(src) == b"START_PRINT EXTRUDER_TEMP=250\nM109 S250\n;T0 in a comment\nTIMELAPSE_TAKE_FRAME\n"


def test_a_short_part_gets_about_five_frames_and_a_tall_one_keeps_the_old_schedule():
    from shop.printwatch import checkpoints
    assert checkpoints(46) == [2, 10, 22, 33, 44]
    assert checkpoints(529) == [2, 10, 50, 100, 200, 300, 400, 500]


def test_checkpoint_due_uses_the_part_s_layer_count():
    assert checkpoint_due(23, {10}, count=46) == 22
    assert checkpoint_due(23, {22}, count=46) is None


SLICES = [{"path": "box_PETG_36m32s.gcode", "modified": 1}, {"path": "box_PETG_42m43s.gcode", "modified": 3},
          {"path": "box_PETG_41m59s.gcode", "modified": 2}, {"path": "boxer.gcode", "modified": 9}]


def test_a_3mf_name_resolves_to_its_newest_slice():
    # 2026-11-25: `shop watch run box.3mf` hit a raw 404 traceback; the printer holds box_PETG_<time>.gcode.
    from shop.printwatch import pick_gcode
    assert pick_gcode("box.3mf", SLICES, None) == "box_PETG_42m43s.gcode"


def test_the_printing_slice_wins_over_the_newest():
    from shop.printwatch import pick_gcode
    assert pick_gcode("box", SLICES, "box_PETG_36m32s.gcode") == "box_PETG_36m32s.gcode"


def test_an_exact_name_is_kept_and_a_missing_one_refused_in_words():
    import pytest
    from shop.printwatch import Refused, pick_gcode
    assert pick_gcode("boxer.gcode", SLICES, None) == "boxer.gcode"
    with pytest.raises(Refused, match="not on the printer"):
        pick_gcode("lid.3mf", SLICES, None)


def test_a_timeout_is_reported_as_a_timeout_not_as_unreachable(monkeypatch, capsys):
    from shop import printwatch as pw

    def slow(a):
        raise TimeoutError("timed out")
    monkeypatch.setattr(pw, "upload", slow)
    assert pw.main(["upload", "x.gcode"]) == 1
    out = capsys.readouterr().out
    assert "timed out" in out and "cannot reach" not in out
