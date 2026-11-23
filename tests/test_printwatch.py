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
