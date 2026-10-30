from src.detectorA import detectorTypeA


def test_ping():
    assert detectorTypeA((5, 5), (6, 7), 2) == "ping"


def test_no_ping():
    assert detectorTypeA((5, 5), (9, 9), 2) == "no ping"


def test_found():
    assert detectorTypeA((5, 5), (5, 5), 2) == "found"


def test_boundary():
    assert detectorTypeA((5, 5), (7, 7), 2) == "ping"
