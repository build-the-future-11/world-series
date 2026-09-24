# Complete local evidence package

The original verified delivery stays immutable. The replacement builder includes
all files under src, tests, scripts, configs, docs, data, experiments, provenance,
results, runs and campaigns, excluding Python bytecode. Failures and interrupted
receipts are included, not silently omitted because a campaign is incomplete.

Original .portfolio source/analysis inputs and project proposals have been copied
byte-for-byte into provenance/. The collection-audit snapshot is also included.
IMPORT_MANIFEST.json records original locations, sizes and hashes. Original
absolute paths are provenance strings; the builder reads package-relative paths.
No environments or external Celo2 weight files are redistributed. The existing
pinned model-fetch record remains in the package. Actual owner licensing choices
and model/data permission review remain unfinished: this is a local review
archive, not an authorized public release.

The verifier reads its Git bundle from the archive and checks it in a temporary
bare repository. It does not need the original checkout or a sidecar bundle.
Every archive member must be a unique regular file with a safe relative path,
matching size and SHA256. Extraction refuses an existing target directory.
Tests exercise relocation, missing sidecar, preserved failed/interrupted runs,
tampered imported evidence, recursive output and path traversal rejection.

Full module plus packaging suite: 98 passed. Numerical source is unchanged from
the CWLNN stage. A subsequent receipt records the actual archive, extracted
environment and commands; this design document is not evidence that installation,
every analysis or every full experiment has reproduced. R02/R05/R10/R11 remain
open until their complete requirements, rather than only archive integrity, pass.
