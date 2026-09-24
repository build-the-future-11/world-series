
from world_series.qwipii.domains import RingState
from world_series.qwipii.discovery import discover_and_verify

def test_adversarial_rejected():
    states = [RingState((1,0,2),(0,1,2)), RingState((2,1,0),(0,1,2))]
    disc = discover_and_verify(states)
    adv = [d for d in disc if d["kind"]=="adversarial"]
    assert adv and adv[0]["label"]=="REJECTED"
    assert any(d["verified"] for d in disc)
