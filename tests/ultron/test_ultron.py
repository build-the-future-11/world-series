
from world_series.ultron.evidence import EvidenceDAG
from world_series.core.contracts import WorldSeriesError
import pytest
def test_evidence_requires_parents():
    dag = EvidenceDAG()
    with pytest.raises(WorldSeriesError):
        dag.add("b", ("a",), {"x":1}, "v")
    dag.add("a", (), {"x":0}, "v")
    dag.add("b", ("a",), {"x":1}, "v")
