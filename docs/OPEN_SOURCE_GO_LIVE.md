# Open-source go-live checklist

Target: public Apache-2.0 release of the workbench + bounded negative-results
preprint. Independent confirmation campaigns are **out of scope** for this gate.

## Done

- [x] Apache-2.0 `LICENSE` + `NOTICE` (implementation and collection)
- [x] `THIRD_PARTY.md` (UCI CC BY 4.0, dependency inventory, Celo2 external)
- [x] `pyproject.toml` license/authors metadata
- [x] Manuscript: contribution/inclusion rule, related work for all nine modules,
      estimand table, exactness caveat, author line, AI responsibility wording
- [x] `docs/HEADLINE_REPRODUCTION.md` + `.json` and `scripts/verify_headline_claims.py`
- [x] `docs/AUTHORSHIP.md` completed and dated (Ryan / 26 September 2026)
- [x] README / release-repro / status docs updated for OSS
- [x] Commit and push both repos; CI green on `world-series`
- [x] Publish hashed review archive on GitHub Release `v0.1.0-oss`
- [x] Set GitHub repos to **Public** (`build-the-future-11/...`)
- [x] Tag `v0.1.0-oss` on both repos
- [x] Archive integrity + restored-source verify (`release_export/20260925/GO_LIVE_RESULTS.json`)
- [x] README badges (license / release / CI)
- [x] `.mailmap` for placeholder → GitHub noreply mapping
- [x] arXiv upload bundle prepared (`paper/arxiv/`)

## Human-only / later

- [ ] Submit `paper/arxiv/arxiv-world-series-v010.tar.gz` at https://arxiv.org/submit
- [ ] Optional local git email for future commits (see `FINAL_OSS_CHECKLIST.md`; no automated git-config edits)

## Do not claim on go-live

- Independent scientific confirmation
- Completion of all nine original architectures
- Novelty of each module versus closest literature beyond attribution
- That a Git clone alone contains raw campaigns
