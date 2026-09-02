# 去重与标签冲突处理日志（Duplicate and Label-Conflict Resolution Log）

> 对应论文 Supplementary Materials 中 "duplicate and label-conflict resolution logs" 一项。
> 记录 processed benchmark 的去重规则、可验证统计，以及无法从当前已发布文件重建的历史处理值。

## 一、去重规则

以 **RDKit-canonical SMILES（`smi_c`）+ 大写蛋白序列（`Protein`）** 作为 drug--target pair 标识：

1. 每条记录的 SMILES 用 RDKit 解析；解析失败（`Chem.MolFromSmiles` 返回 None）的样本剔除。
2. 解析成功的 SMILES 转为 canonical 形式。
3. 蛋白序列统一转大写。
4. 对 `(smi_c, Protein)` 完全相同的 pair 去重；若同 pair 携带不同标签（Y 冲突），**保留正类（Y=1）**。

实现见 `code/build_splits.py`（`prepare()` / `dedup()`）。

## 二、当前已发布文件的验证统计（2026-09-02 重算）

以下统计直接作用于本仓库 `data/` 下已发布的划分 CSV（train/val/test 合并后按 pair 标识复检）：

| 数据集 / 划分 | 合并后样本 | SMILES 解析失败 | 重复 pair（含标签一致） | 标签冲突 pair | 唯一药物 | 唯一蛋白 |
|---|---|---|---|---|---|---|
| biosnap / random | 27,457 | 0 | 0 | 0 | 4,505 | 2,181 |
| biosnap / unseen_drug | 27,457 | 0 | 0 | 0 | 4,505 | 2,181 |
| biosnap / unseen_target | 27,457 | 0 | 0 | 0 | 4,505 | 2,181 |
| bindingdb / random | 49,199 | 0 | 0 | 0 | 14,643 | 2,623 |

> 已发布文件内部不再含重复/冲突 pair，因为**去重发生在划分（7:1:2 / 实体互斥）之前**：原始全量交互集先按上述规则去重，再去重后样本做划分。因此对划分后 CSV 复检必然为零。

## 三、历史处理记录值（划分前，不可从已发布文件重建）

划分前对**原始全量交互集**执行去重时的记录值（处理管线日志，原始全量文件未随本仓库发布）：

- **BioSNAP：去重 7 对**（原始交互集中重复/冲突的 pair 数）。
- **BindingDB：去重对数为 0**（原始文件已无重复）。

这两个数值来自处理时的管线输出（`build_splits.py` 打印的 `原始样本 ... | 去重后 ...（冲突标签 N）`），因原始全量源文件未归档，无法从当前已发布划分文件独立重现；在本说明中如实披露，不伪造可复现性。

## 四、对审稿人的影响说明

论文 Data Availability 声明 "duplicate pairs were removed (seven pairs in BioSNAP; conflicting labels retained the positive label)" 中的 **"seven pairs" 指划分前原始交互集的去重对数**，即本表第三部分的历史记录值，不是已发布文件内的重复数（后者为 0）。
