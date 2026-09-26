# arXiv upload package

Bundle: `arxiv-world-series-v010.tar.gz`

## Contents
- `preprint.tex` (generated from `../preprint.md`)
- `figures/wfim-paired-seeds.png`

## Upload steps (human; requires arXiv account)
1. Go to https://arxiv.org/submit
2. Choose license compatible with Apache-2.0 dual distribution (often arXiv perpetual non-exclusive / CC options as required by arXiv UI)
3. Upload `arxiv-world-series-v010.tar.gz` as the TeX source package
4. Category suggestion: `cs.LG` (primary); optional `stat.ML`
5. Title/abstract: copy from `../preprint.md`
6. Comments: "Source-bound negative-results / mechanism-verification case study. Code: https://github.com/build-the-future-11/world-series"
7. After acceptance, add the arXiv id to the GitHub release notes and README badge

## Build locally
```sh
cd paper
pandoc preprint.md --standalone -V geometry:margin=0.85in -V fontsize=11pt -V papersize=a4 -o preprint.tex
# then refresh this bundle from preprint.tex + figures/
```
