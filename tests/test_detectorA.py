from src.detectorA import detectorTypeA


def test_ping():
    assert detectorTypeA((5, 5), (6, 7), 2) == "ping"
#this tests when the lostbot is within the detector range

def test_no_ping():
    assert detectorTypeA((5, 5), (9, 9), 2) == "no ping"
#this part tests when the lostbot is outside the detector range

def test_found():
    assert detectorTypeA((5, 5), (5, 5), 2) == "found"
#this tests both bots are in the same postion

def test_boundary():
    assert detectorTypeA((5, 5), (7, 7), 2) == "ping"
#this tests when the lostbot is on the boundary of the detector range