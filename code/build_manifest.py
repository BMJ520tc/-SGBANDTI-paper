# -*- coding: utf-8 -*-
"""生成唯一 results_manifest.csv（P0-2 证据链冻结）。
数据源：
  - SGBANDTI / DrugBAN 逐 seed：stats_input/（配对 bootstrap 用的逐样本 y_pred/y_true）
  - SGBANDTI 消融配置：本地 result/*/seed_*/result_metrics.pt（full/no_subgraph/no_both 全 5 seed）
  - 其他基线：交付包 00_实验结果汇总.md 的 mean ± sample SD（ddof=1）
差异以 stats_input 逐样本为准（可复现）；若与 00_汇总不一致，在 source 列注明。
用法：在仓库根运行，输出到 ./results/results_manifest.csv（可用环境变量 SGBANDTI_OUT_DIR 覆盖输出目录）。
数据源为仓库内相对路径（stats_input/、result/）；若对应逐样本/结果目录缺失，相应行留空。"""
import os
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

SEEDS = [42, 52, 62, 72, 82]
ROWS = []


def stats_seed(setting, model):
    """从 stats_input 算逐 seed AUROC/AUPRC，返回 (auroc_per_seed, auprc_per_seed)。"""
    a, p = [], []
    for s in SEEDS:
        fp = f'stats_input/{setting}/{model}/seed_{s}_y_pred.npy'
        ft = f'stats_input/{setting}/{model}/seed_{s}_y_true.npy'
        if os.path.exists(fp):
            yp = np.load(fp); yt = np.load(ft)
            a.append(roc_auc_score(yt, yp)); p.append(average_precision_score(yt, yp))
    return (np.array(a) if a else None), (np.array(p) if p else None)


def emit(ds, sp, model, cfg, auroc, auprc, source, pred_file='', true_file=''):
    """auroc/auprc 是逐 seed 数组或 None(仅 mean±std 已知)。"""
    def sstats(x):
        if x is None or len(x) == 0:
            return '', ''
        return f'{x.mean():.4f}', f'{x.std(ddof=1):.4f}'
    am, asd = sstats(auroc); pm, psd = sstats(auprc)
    a5 = [f'{v:.4f}' if auroc is not None and len(auroc) > i else '' for i, v in enumerate(auroc if auroc is not None else [])]
    p5 = [f'{v:.4f}' if auprc is not None and len(auprc) > i else '' for i, v in enumerate(auprc if auprc is not None else [])]
    ROWS.append({
        'dataset': ds, 'split': sp, 'model': model, 'config': cfg,
        'auroc_mean': am, 'auroc_std': asd, 'auprc_mean': pm, 'auprc_std': psd,
        'auroc_s42': a5[0] if a5 else '', 'auroc_s52': a5[1] if len(a5) > 1 else '',
        'auroc_s62': a5[2] if len(a5) > 2 else '', 'auroc_s72': a5[3] if len(a5) > 3 else '',
        'auroc_s82': a5[4] if len(a5) > 4 else '',
        'auprc_s42': p5[0] if p5 else '', 'auprc_s52': p5[1] if len(p5) > 1 else '',
        'auprc_s62': p5[2] if len(p5) > 2 else '', 'auprc_s72': p5[3] if len(p5) > 3 else '',
        'auprc_s82': p5[4] if len(p5) > 4 else '',
        'pred_file': pred_file, 'true_file': true_file, 'source': source,
    })


SETTINGS = [('biosnap', 'random'), ('bindingdb', 'random'),
            ('biosnap', 'unseen_drug'), ('biosnap', 'unseen_target')]
ST_DIR = {
    ('biosnap', 'random'): 'biosnap_random', ('bindingdb', 'random'): 'bindingdb_random',
    ('biosnap', 'unseen_drug'): 'biosnap_unseen_drug', ('biosnap', 'unseen_target'): 'biosnap_unseen_target',
}

# 1) SGBANDTI / DrugBAN：4 场景逐 seed（stats_input）
for (ds, sp), st in ST_DIR.items():
    for model in ['SGBANDTI', 'DrugBAN']:
        a, p = stats_seed(st, model)
        if a is None:
            continue
        emit(ds, sp, model, 'full', a, p,
             source=f'stats_input/{st}/{model}/seed_*_y_pred.npy（逐样本重算）',
             pred_file=f'stats_input/{st}/{model}/', true_file=f'stats_input/{st}/{model}/')

# 2) SGBANDTI 消融（biosnap random full/no_subgraph/no_both/gcn_tokens：results/per_seed 全 5 seed）
import torch, os
PER = os.path.join('results', 'per_seed')
ABL = {'no_subgraph': 'biosnap_random_hop2_no_subgraph',
       'no_ban': 'biosnap_random_hop2_no_ban',
       'no_both': 'biosnap_random_hop2_no_both',
       'gcn_tokens': 'biosnap_random_hop2_gcn_tokens'}
for cfg, d in ABL.items():
    a, p = [], []
    for s in SEEDS:
        f = os.path.join(PER, f'{d}', f'seed_{s}', 'result_metrics.pt')
        if os.path.exists(f):
            m = torch.load(f, map_location='cpu', weights_only=False)['test_metrics']
            a.append(m['auroc']); p.append(m['auprc'])
    if a:
        emit('biosnap', 'random', 'SGBANDTI', cfg, np.array(a), np.array(p),
             source=f'results/per_seed/{d}/seed_*/result_metrics.pt（本地复现）')

# 2.5) biosnap random 基线（MGNDTI/MolTrans/TransformerCPI）：per_seed 逐样本重算（5 seed）
PER_BASE = {'MGNDTI': 'MGNDTI_biosnap', 'MolTrans': 'MolTrans_biosnap',
            'TransformerCPI': 'TransCPI_biosnap'}
for name, d in PER_BASE.items():
    a, p = [], []
    for s in SEEDS:
        fp = os.path.join(PER, d, f'seed_{s}', 'y_pred.npy')
        ft = os.path.join(PER, d, f'seed_{s}', 'y_true.npy')
        if os.path.exists(fp) and os.path.exists(ft):
            yp = np.load(fp); yt = np.load(ft)
            a.append(roc_auc_score(yt, yp)); p.append(average_precision_score(yt, yp))
    if a:
        emit('biosnap', 'random', name, 'full', np.array(a), np.array(p),
             source=f'results/per_seed/{d}/seed_*/y_pred.npy（逐样本重算）',
             pred_file=f'results/per_seed/{d}/', true_file=f'results/per_seed/{d}/')

# 3) 其他基线：00_汇总 mean ± sample SD（ddof=1）；已被 per_seed 逐样本覆盖的不再重复
OTHER = {
    ('biosnap', 'random'): {'INGNN': (0.8720, 0.0007, 0.8771, 0.0013),
                            'RF': (0.8402, 0.0008, 0.8678, 0.0007),
                            'GNN-CPI': (0.7088, 0.0036, 0.7229, 0.0010)},
    ('bindingdb', 'random'): {'MGNDTI': (0.9500, 0.0014, 0.9326, 0.0021),
                              'RF': (0.9407, 0.0004, 0.9209, 0.0005), 'MolTrans': (0.9338, 0.0017, 0.9086, 0.0054),
                              'INGNN': (0.9228, 0.0028, 0.8951, 0.0024), 'TransformerCPI': (0.8921, 0.0012, 0.8556, 0.0016),
                              'GNN-CPI': (0.6548, 0.1712, 0.5782, 0.2045)},
    ('biosnap', 'unseen_drug'): {'MGNDTI': (0.8589, 0.0057, 0.8675, 0.0038), 'RF': (0.8493, 0.0006, 0.8724, 0.0005),
                                 'TransformerCPI': (0.8460, 0.0113, 0.8551, 0.0061), 'INGNN': (0.8417, 0.0057, 0.8510, 0.0023),
                                 'MolTrans': (0.8407, 0.0082, 0.8473, 0.0057), 'GNN-CPI': (0.6797, 0.0897, 0.6795, 0.0933)},
    ('biosnap', 'unseen_target'): {'RF': (0.6979, 0.0110, 0.6867, 0.0068), 'MGNDTI': (0.6910, 0.0105, 0.6836, 0.0168),
                                   'MolTrans': (0.6820, 0.0166, 0.6788, 0.0193), 'INGNN': (0.6526, 0.0090, 0.6421, 0.0075),
                                   'GNN-CPI': (0.6501, 0.0030, 0.6526, 0.0017), 'TransformerCPI': (0.6160, 0.0319, 0.6032, 0.0216)},
}
for (ds, sp), models in OTHER.items():
    for name, (am, asd, pm, psd) in models.items():
        emit(ds, sp, name, 'full', None, None,
             source=f'00_实验结果汇总.md（mean±sample SD，ddof=1；逐 seed 未公开归档）')
        ROWS[-1]['auroc_mean'] = f'{am:.4f}'; ROWS[-1]['auroc_std'] = f'{asd:.4f}'
        ROWS[-1]['auprc_mean'] = f'{pm:.4f}'; ROWS[-1]['auprc_std'] = f'{psd:.4f}'

COLS = ['dataset', 'split', 'model', 'config', 'auroc_mean', 'auroc_std', 'auprc_mean', 'auprc_std',
        'auroc_s42', 'auroc_s52', 'auroc_s62', 'auroc_s72', 'auroc_s82',
        'auprc_s42', 'auprc_s52', 'auprc_s62', 'auprc_s72', 'auprc_s82',
        'pred_file', 'true_file', 'source']
out = os.path.join(os.environ.get('SGBANDTI_OUT_DIR', 'results'), 'results_manifest.csv')
pd.DataFrame(ROWS, columns=COLS).to_csv(out, index=False, encoding='utf-8')
print('written:', out, 'rows:', len(ROWS))
print(pd.read_csv(out).to_string(index=False))
