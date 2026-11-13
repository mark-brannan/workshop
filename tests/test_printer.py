from shop.printer import format_status

STATUS = {
    "webhooks": {"state": "ready"},
    "print_stats": {"filename": "part.gcode", "state": "printing", "print_duration": 1800.0},
    "virtual_sdcard": {
        "progress": 0.5,
        "layer": 47,
        "layer_count": 94,
        "cur_print_data": {"metadata": {"estimated_time": 3860, "filament_type": "PETG", "layer_height": 0.24}},
    },
    "extruder": {"temperature": 139.77, "target": 140.0, "nozzle_diameter": 0.4},
    "heater_bed": {"temperature": 30.25, "target": 50.0},
    "temperature_sensor chamber_temp": {"temperature": 16.61},
    "heater_generic chamber_heater": {"target": 0.0, "power": 0.0},
    "toolhead": {"position": [175.0, 175.0, 4.988, 0.0], "homed_axes": "xyz"},
    "filament_switch_sensor filament_sensor": {"filament_detected": True},
    "output_pin fan0": {"value": 0.5},
    "output_pin fan1": {"value": 0.0},
    "output_pin fan2": {"value": 1.0},
    "fan_feedback": {"fan0_speed": 4000, "fan1_speed": 0, "fan2_speed": 9000},
    "heater_fan hotend_fan": {"speed": 1.0},
}


def test_status_reports_job_progress_and_temperatures():
    out = format_status(STATUS)
    assert "printing  part.gcode" in out
    assert "50%  layer 47/94  0h30m of ~1h04m" in out
    assert "139.8 / 140 C" in out and "30.2 / 50 C" in out
    assert "chamber  16.6 C" in out
    assert "part 50% (4000 tach)  chamber 0% (0 tach)  aux 100% (9000 tach)  hotend 100%" in out


def test_idle_printer_skips_job_lines():
    idle = {**STATUS, "print_stats": {"filename": "", "state": "standby", "print_duration": 0}}
    out = format_status(idle)
    assert "standby  -" in out and "progress" not in out


def test_missing_optional_objects_are_tolerated():
    bare = {k: v for k, v in STATUS.items() if k not in ("temperature_sensor chamber_temp", "filament_switch_sensor filament_sensor")}
    out = format_status(bare)
    assert "chamber  " not in out and "filament " not in out
