from __future__ import annotations
from world_series.wcode.interpreter import interpret, Fuel, validate_ast

def verify_program(prog, tests: list[tuple[dict, int]], exhaustive_domain: list[int] | None = None) -> dict:
    validate_ast(prog)
    for env, y in tests:
        if interpret(prog, env, Fuel(128)) != y:
            return {"ok": False, "scope": "HELDOUT_TESTS"}
    if exhaustive_domain is not None:
        # example: programs of form x+1 over a finite domain
        for x in exhaustive_domain:
            # only meaningful if prog uses x; still record scope
            interpret(prog, {"x": x}, Fuel(64))
        return {"ok": True, "scope": "HELDOUT_TESTS_PLUS_DOMAIN_EXECUTION", "domain_size": len(exhaustive_domain)}
    return {"ok": True, "scope": "HELDOUT_TESTS"}
