#!/bin/bash
# SGBANDTI 一键生成链: 数据校验 → manifest → 图表 → LaTeX
# 用法: bash run_all.sh [--skip-latex]   (在仓库根运行)
set -e
cd "$(dirname "$0")"
PY="python"
TEX_DIR="MDPI_template_ACS/MDPI_template_ACS"

echo "[1/4] 数据校验 (与 SPLITS_FROZEN 样本数核对)"
python - <<'PYEOF'
import pandas as pd
expected = {
    ('biosnap','random'): (19220, 2746, 5491),
    ('biosnap','unseen_drug'): (19372, 2795, 5290),
    ('biosnap','unseen_target'): (19980, 2574, 4903),
    ('bindingdb','random'): (34439, 4920, 9840),
}
ok = True
for (ds, sp), exp in expected.items():
    try:
        n = [len(pd.read_csv(f'datasets/{ds}/{sp}/{k}.csv')) for k in ('train','val','test')]
    except Exception as e:
        print(f'  [缺] {ds}/{sp}: {e}'); ok = False; continue
    m = n == list(exp)
    ok = ok and m
    print(f'  {"OK" if m else "FAIL"} {ds}/{sp}: {n} (期望 {list(exp)})')
print('数据校验:', '通过 ✅' if ok else '失败 ❌')
raise SystemExit(0 if ok else 1)
PYEOF

echo "[2/4] 生成 results_manifest.csv"
SGBANDTI_OUT_DIR="${SGBANDTI_OUT_DIR:-./results}" $PY build_manifest.py

echo "[3/4] 生成图表"
cd "$TEX_DIR"
$PY generate_ablation_figure.py
$PY generate_split_figure.py

if [[ "$1" != "--skip-latex" ]]; then
  echo "[4/4] LaTeX 编译"
  latexmk -pdf -interaction=nonstopmode manuscript_mdpi.tex > /dev/null 2>&1 || pdflatex -interaction=nonstopmode manuscript_mdpi.tex > /dev/null 2>&1
  grep -m1 "Output written" manuscript_mdpi.log
else
  echo "[4/4] 跳过 LaTeX"
fi
echo "=== 一键生成链完成 ==="
