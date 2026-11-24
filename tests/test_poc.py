"""The POC must be honest by construction: a range, not a rate."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import poc


def test_band_scales_with_the_count():
    assert poc.band(0, .03, .03) == 0
    assert poc.band(100, .03, .03) == 6
    assert poc.band(10, .03, .03) == 1


def test_signal_below_camera_error_is_not_quoted_as_a_rate():
    """10 boardings, 9 taps, 3%+3% error -> band of 1, so 1 no-tap is not a finding."""
    t = poc.trip_summary(10, 9)
    assert t['unpaid_est'] == 1 and t['band'] == 1
    assert t['reliable'] is False
    assert 'inside camera error' in t['verdict']


def test_clear_signal_is_flagged():
    t = poc.trip_summary(100, 80)
    assert t['unpaid_est'] == 20 and t['low'] == 14 and t['high'] == 26
    assert t['reliable'] is True


def test_more_taps_than_boardings_never_goes_negative():
    t = poc.trip_summary(5, 9)
    assert t['unpaid_est'] == 0 and t['low'] == 0


def test_per_stop_rows_cover_every_stop_and_a_clean_stop():
    boards = [{'stop': 1, 'type': 'board'}] * 12 + [{'stop': 2, 'type': 'board'}] * 10
    payments = [{'stop': 1, 'method': 'app'}] * 12 + [{'stop': 2, 'method': 'rav-kav'}] * 5
    rows = {r['stop']: r for r in poc.per_stop(boards, payments, .03, .03)}
    assert rows['1']['unpaid_est'] == 0
    assert rows['2']['unpaid_est'] == 5 and rows['2']['reliable'] is True


def test_payments_csv_reading_is_tolerant():
    import tempfile, pathlib
    p = pathlib.Path(tempfile.mkdtemp()) / "pay.csv"
    p.write_text("stop,method\n1,app\n1,qr\n2,rav-kav\n")
    rows = poc.read_payments(str(p))
    assert len(rows) == 3 and rows[0]['stop'] == '1'
    assert poc.read_payments(None) == []


class _T:
    """Minimal track stand-in: pred() returns the predicted box."""
    def __init__(self, box): self.box = box
    def pred(self): return self.box


def test_distance_match_recovers_a_jittered_person():
    """IoU fails when a box shifts; centre distance should still hold the ID."""
    from track_util import match_by_distance
    t = _T((100, 100, 140, 200))
    jittered = (108, 104, 148, 204)          # same person, box shifted
    assert match_by_distance([t], [jittered]) == [(0, 0)]


def test_distance_match_refuses_a_distant_box():
    from track_util import match_by_distance
    t = _T((100, 100, 140, 200))
    far = (400, 100, 440, 200)
    assert match_by_distance([t], [far]) == []


def test_distance_match_is_one_to_one():
    from track_util import match_by_distance
    a, b = _T((100, 100, 140, 200)), _T((300, 100, 340, 200))
    assert len(match_by_distance([a, b], [(104, 100, 144, 200), (304, 100, 344, 200)])) == 2
