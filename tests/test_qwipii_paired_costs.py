"""Regression tests for the QWIPII paired cost-analysis utility."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "qwipii_paired_costs.py"
spec = importlib.util.spec_from_file_location("qwipii_paired_costs", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def rows():
    return [
        {"family": fam, "instance": str(i), "method": method,
         "solved": True, "optimal": True, "runtime_ms": ms}
        for fam in ("A", "B", "C") for i in (1, 2)
        for method, ms in (("brute", 2.0), ("learned", 1.0))
    ]


def test_ratio():
    result = module.compare(rows(), bootstrap=100)
    assert result["family_count"] == 3
    assert result["paired_instances"] == 6
    assert abs(result["family_equal_weight_geomean_ratio"] - 0.5) < 1e-12


def test_incorrect_path_rejected():
    data = rows()
    data[0]["optimal"] = False
    with pytest.raises(ValueError, match="incorrect"):
        module.compare(data)


def test_duplicate_rejected():
    data = rows()
    with pytest.raises(ValueError, match="duplicate"):
        module.compare(data + [dict(data[0])])


def test_missing_baseline_rejected():
    data = [r for r in rows() if not (
        r["family"] == "A" and r["instance"] == "1" and r["method"] == "brute"
    )]
    with pytest.raises(ValueError, match="unpaired"):
        module.compare(data)


def test_amortized_cost():
    data = rows()
    for r in data:
        if r["method"] == "learned":
            r["offline_ms"] = 20.0
            r["planned_queries"] = 2
    assert module.compare(data, bootstrap=50)["family_equal_weight_geomean_ratio"] > 1


def test_bootstrap_validation():
    with pytest.raises(ValueError, match="bootstrap"):
        module.compare(rows(), bootstrap=1)


def test_reverse_unpaired_baseline_rejected():
    data = [r for r in rows() if not (
        r["family"] == "A" and r["instance"] == "1" and r["method"] == "learned"
    )]
    with pytest.raises(ValueError, match="unpaired"):
        module.compare(data)


def test_one_family_no_inferential_interval():
    data = [r for r in rows() if r["family"] == "A"]
    result = module.compare(data, bootstrap=50)
    assert result["family_bootstrap_95pct_ratio"] is None
    assert "one independent family" in result["uncertainty_warning"].lower()


def test_methods_must_differ():
    with pytest.raises(ValueError, match="differ"):
        module.compare(rows(), candidate="brute", baseline="brute")
