# SPLITS_FROZEN（最终数据划分冻结记录）

Git commit: `release-tag-pending`（原主仓库引用 commit `5d93e6c` 不在本公开仓库历史中，随本仓库发布 release/tag 时绑定）

| 划分 | split 样本数(t/v/te) | 药物 | 蛋白 | 正/负 | md5(train/val/test) |
|---|---|---|---|---|---|
| bindingdb/random | 34439/4920/9840 | 14643 | 2623 | 20674/28525 | 5c3f4eed/9d4dafe2/cdcfc9e8 |
| biosnap/random | 19220/2746/5491 | 4505 | 2181 | 13830/13627 | f5b232de/452f3334/1426fdeb |
| biosnap/unseen_drug | 19372/2795/5290 | 4505 | 2181 | 13830/13627 | b576e0bc/afe9ec28/5af9ddfc |
| biosnap/unseen_target | 19980/2574/4903 | 4505 | 2181 | 13830/13627 | a501bf4d/8fae4532/1e35c17c |
