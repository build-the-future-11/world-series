# Evidence preservation repair — 10 October 2026

This is an engineering repair against `a7ab171465aa92aec57e2079f8df71e7685d4cf9`.
Historical scientific results, protocols, datasets, source archives, and the nine
projects' scientific conclusions are unchanged. New runs identify the changed
source through the existing source-content hash.

## Demonstrated defects

Forty cases in `tests/core/test_evidence_preservation.py` failed against the
unchanged source; its ordinary negative-result round trip passed. The failures
include overwritten prediction artifacts, two concurrent writers both reporting
success, a followed dangling output symlink, terminal receipts rewritten after
failure/interruption, mutable metrics changing the final manifest, and invalid
budgets or negative consumption crediting resources.

## Implemented behavior

- Stage complete artifact bytes on the destination filesystem and publish with
  an atomic no-replacement hard link. Existing paths and losing writers survive.
- Replace a still-active manifest atomically; seal terminal receipts and metrics.
  An identical repeated terminal status is a no-op, preserving the finish time.
- Copy metrics and error dictionaries before retaining them, preventing later
  caller mutation from changing the manifest.
- Require finite nonnegative wall budgets and integer resource/count budgets.
  Reject invalid consumption before counters change.
- Record a CLI `KeyboardInterrupt` as `INTERRUPTED`, retain partial evidence, and
  return exit status 130. Ordinary successful execution can still record a
  `NOT_SUPPORTED` scientific result.

## Verification and limits

Local focused command:

```bash
python -m pytest tests/core/test_evidence_preservation.py tests/core/test_cli_interruption.py tests/core/test_runner.py tests/core/test_contracts.py tests/core/test_json_config.py -q -o addopts=''
```

Result: **50 passed**, including real concurrent publication and CLI interruption
fault injection. Critical static checks and patch whitespace checks passed.
The complete model suite requires PyTorch, unavailable in this local runtime;
the existing hosted implementation workflow remains responsible for that gate.
No scientific campaign was rerun to obtain these software checks.

The mutable manifest is owned by one numerical worker, as required by this
repository. Atomic artifact publication is safe for concurrent publishers, but
does not add multi-writer transactions around an entire run. Parent directories
remain trusted. A filesystem that cannot create hard links fails without
replacement. Atomic visibility does not establish power-loss durability.
