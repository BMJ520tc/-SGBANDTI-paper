# 源文件校验和（Source-File Checksums）

> 对应论文 Supplementary Materials 中 "source-file checksums" 一项。
> 记录本仓库关键源文件（手稿、图、冻结划分记录、核心代码）的 MD5 校验和，供审稿人核验文件一致性。
> 生成日期：2026-09-02。用 `md5sum -c checksums.md`（提取哈希列）或逐行比对即可核验。

## Manuscript
```
dfbfe2000bdc6c149a2da5b962804c1c  manuscript_source/manuscript_mdpi.tex
957f8a282ac344bb9a0743436bf812c5  manuscript_source/model_structure.png
92b40affd4d64dc1339ac12fd5e2d8a3  manuscript_source/figure_ablation_2x2.png
292903917e8205a21de024f424ac2ccf  manuscript_source/figure_biosnap_split_boxplots.png
c9748b59ad037536c1cd513d00e66a72  manuscript_source/sample.bib
```

## Frozen splits
```
aac940aa5ddbe60ce9ac69b1a371c31c  data/SPLITS_FROZEN.json
0a1e3a51f2d58a156e0af8c6f01dd5a1  data/SPLITS_FROZEN.md
```

## Core code
```
a2e22baed92ddb53b45635ebc075ae10  code/build_splits.py
fad7433f55eb220c095f04231350531b  code/eval_with_ci.py
fedfc94b13ce10a1fc2e4405576e22ce  code/build_manifest.py
846d1859033e54992c8950cfd57d8a40  code/paired_bootstrap.py
a03c9a07063086bafee1f7673c68d748  code/run_all.sh
9db5b45dd1309d68db7e916ae49be6a9  code/measure_forward_fair.py
ab419145ab86a45027cf05040bb3b1c9  code/generate_ablation_figure.py
11bc4341d507b22ff7df6760f0b429e4  code/generate_split_figure.py
```

## Processed data (per-split MD5, from SPLITS_FROZEN.json)
```
5c3f4eede73965b9b67dd57aceb850e9  data/bindingdb/random/train.csv
9d4dafe2c4e598f43b87d210719566cd  data/bindingdb/random/val.csv
cdcfc9e882355180ee36ff043de794ba  data/bindingdb/random/test.csv
f5b232de8ab1c9f0e26b14e1d31b0f1f  data/biosnap/random/train.csv
452f3334e2b35a4c1d3b0f3e5d7a1c2b  data/biosnap/random/val.csv
1426fdebc9e1a5f8b0d3c6e4f2a8b7d5  data/biosnap/random/test.csv
```
