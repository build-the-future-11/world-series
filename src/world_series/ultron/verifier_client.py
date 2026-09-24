from __future__ import annotations

# Map task types to the only operations that can satisfy the verifier.
_TASK_OPS = {
    "invariant_puzzle": {"solve_invariant_problem"},
    "dsl_synthesis": {"synthesize_dsl_program"},
    "law_id": {"identify_dynamical_law"},
}


def local_dev_verifier(task_type: str, diagnostics: dict, selected_op: str | None = None) -> dict:
    """PLUMBING_ONLY — not a sealed external evaluation.

    Requires both task-appropriate operation (when provided) and task-specific evidence fields.
    """
    if task_type not in _TASK_OPS:
        return {"ok": False, "tag": "PLUMBING_ONLY", "reason": "unsupported_task_type"}
    if selected_op is not None and selected_op not in _TASK_OPS[task_type]:
        return {
            "ok": False,
            "tag": "PLUMBING_ONLY",
            "reason": "mismatched_operation",
            "selected_op": selected_op,
        }
    if task_type == "invariant_puzzle":
        ok = bool(diagnostics.get("lifted_ok") or diagnostics.get("path"))
        return {"ok": ok, "tag": "PLUMBING_ONLY"}
    if task_type == "dsl_synthesis":
        return {"ok": bool(diagnostics.get("found")), "tag": "PLUMBING_ONLY"}
    if task_type == "law_id":
        return {"ok": "coef" in diagnostics, "tag": "PLUMBING_ONLY"}
    return {"ok": False, "tag": "PLUMBING_ONLY", "reason": "unsupported"}
