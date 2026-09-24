
from world_series.core.seeds import SeedBundle, SeededStreams
from world_series.core.devices import select_device, probe_devices

def test_seed_streams_independent():
    b = SeedBundle.from_master(123)
    s = SeededStreams(b)
    a = s.data.normal(size=5)
    s2 = SeededStreams(b)
    assert (a == s2.data.normal(size=5)).all()

def test_device_cpu_fallback():
    d = select_device("cpu")
    assert d.name == "cpu"
    assert probe_devices()
