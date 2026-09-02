# -*- coding: utf-8 -*-
"""统计收尾: SGBANDTI vs DrugBAN 全场景配对 bootstrap runner。
输入: stats_input/<setting>/SGBANDTI|DrugBAN/seed_<s>_{y_true,y_pred}.npy
实验室把逐样本 .npy 按此结构放进 stats_input/ 后, 运行本脚本即可。
"""
import os
import sys
import subprocess

SETTINGS = ["biosnap_random", "bindingdb_random", "biosnap_unseen_drug", "biosnap_unseen_target"]
SEEDS = [42, 52, 62, 72, 82]
BASE = "stats_input"


def run_pair(setting, seed):
    sgb_y = f"{BASE}/{setting}/SGBANDTI/seed_{seed}_y_pred.npy"
    sgb_t = f"{BASE}/{setting}/SGBANDTI/seed_{seed}_y_true.npy"
    db_y = f"{BASE}/{setting}/DrugBAN/seed_{seed}_y_pred.npy"
    if not all(os.path.exists(f) for f in (sgb_y, sgb_t, db_y)):
        return None
    r = subprocess.run(
        [sys.executable, "paired_bootstrap.py",
         "--y-true", sgb_t, "--a", sgb_y, "--name-a", "SGBANDTI",
         "--b", db_y, "--name-b", "DrugBAN", "--seed", str(seed)],
        capture_output=True, text=True)
    return r.stdout.strip()


import numpy as np

for setting in SETTINGS:
    print(f"\n{'='*55}\n{setting}\n{'='*55}")
    deltas = {"AUROC": [], "AUPRC": []}
    for s in SEEDS:
        out = run_pair(setting, s)
        if out is None:
            print(f"  seed {s}: 缺逐样本, 跳过")
            continue
        print(f"  seed {s}: {out}")
        for line in out.splitlines():
            for m in ("AUROC", "AUPRC"):
                if line.startswith(m) and "Δ=" in line:
                    try:
                        deltas[m].append(float(line.split("Δ=")[1].split()[0]))
                    except (ValueError, IndexError):
                        pass
    if deltas["AUROC"]:
        print(f"\n  → ΔAUROC(SGB−DrugBAN): " + " ".join(f"{d:+.4f}" for d in deltas["AUROC"])
              + f"   均值 {np.mean(deltas['AUROC']):+.4f}")
        print(f"  → ΔAUPRC(SGB−DrugBAN): " + " ".join(f"{d:+.4f}" for d in deltas["AUPRC"])
              + f"   均值 {np.mean(deltas['AUPRC']):+.4f}")
