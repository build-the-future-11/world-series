# Open-source go-live checklist

Target: public Apache-2.0 release of the workbench + bounded negative-results
preprint. Independent confirmation campaigns are **out of scope** for this gate.

## Done in packaging work

- [x] Apache-2.0 `LICENSE` + `NOTICE` (implementation and collection)
- [x] `THIRD_PARTY.md` (UCI CC BY 4.0, dependency inventory, Celo2 external)
- [x] `pyproject.toml` license/authors metadata
- [x] Manuscript: contribution/inclusion rule, related work for all nine modules,
      estimand table, exactness caveat, author line, AI responsibility wording
- [x] `docs/HEADLINE_REPRODUCTION.md` + `.json` and `scripts/verify_headline_claims.py`
- [x] `docs/AUTHORSHIP.md` human sign-off template
- [x] README / release-repro / status docs updated for OSS

## You must finish (human / GitHub)

- [ ] Complete and date `docs/AUTHORSHIP.md` sign-off
- [ ] Prefer a real contact email in Git history / GitHub profile (placeholder emails are not required for Apache-2.0 but look incomplete)
- [ ] Commit and push both repos; confirm CI green on `world-series`
- [ ] Attach or publish the hashed review archive (`world-series-review.tar.gz`) as a GitHub Release asset with SHA-256 in the notes
- [ ] Set GitHub repos to **Public**
- [ ] Optional: submit `paper/preprint` sources to arXiv (TeX from pandoc+tectonic)
- [ ] Optional: tag `v0.1.0-oss` on both repos

## Do not claim on go-live

- Independent scientific confirmation
- Completion of all nine original architectures
- Novelty of each module versus closest literature beyond attribution
- That a Git clone alone contains raw campaigns
