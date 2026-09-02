# 源文件校验和（Source-File Checksums）

> 对应论文 Supplementary Materials 中 source-file checksums 一项。
> MD5 按 git 检出后的 LF 规范化文件计算（见 .gitattributes）。
> 重新生成日期：2026-09-02（第10版评审 S3/S4 后）。

## Manuscript
```
5368e88d9c2ea6bfc7887efcc2e52d13  manuscript_source/manuscript_mdpi.tex
957f8a282ac344bb9a0743436bf812c5  manuscript_source/model_structure.png
92b40affd4d64dc1339ac12fd5e2d8a3  manuscript_source/figure_ablation_2x2.png
292903917e8205a21de024f424ac2ccf  manuscript_source/figure_biosnap_split_boxplots.png
c9748b59ad037536c1cd513d00e66a72  manuscript_source/sample.bib
```

## Frozen splits
```
f34c8b0d4c34d30d05e5bf5331d188a1  data/SPLITS_FROZEN.json
17bc919adc9d26248219333c1e1b6efe  data/SPLITS_FROZEN.md
```

## Core code
```
a2e22baed92ddb53b45635ebc075ae10  code/build_splits.py
fad7433f55eb220c095f04231350531b  code/eval_with_ci.py
a67be095304a8913666d6c99353cab72  code/build_manifest.py
846d1859033e54992c8950cfd57d8a40  code/paired_bootstrap.py
92054b2ae98c1bb8bb142842ef313091  code/run_paired_bootstrap_all.py
8ef619a54c174586af03f0dfc6e01d2f  code/run_all.sh
7189e2927c3dc8b0d91de6cab447a5f5  code/measure_forward_fair.py
bc103adf12b2e19b26aac62ba7a4c4d8  code/measure_efficiency.py
ad047ba99a7cbfb65ee0495fdc3bd528  code/generate_ablation_figure.py
0e582d7b74a920eceb2fbbe25c2e0bb8  code/generate_split_figure.py
42295692ae5e071a8844784573ab6baf  code/gcn.py
fa6b29a68be4041284b69647b585bce0  code/models.py
8c64bbcbf3b0adcd326df0396d030763  code/configs.py
74003a90386207249513a3c8b954ef5e  code/main.py
```
