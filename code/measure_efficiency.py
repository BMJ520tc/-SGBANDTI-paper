# -*- coding: utf-8 -*-
"""测量 SGBANDTI-full / no-subgraph / DrugBAN 在 RTX4060、batch64、BioSNAP random 下的
参数量 / 单 epoch 训练时间(300 batch) / 峰值显存 / 推理速度。"""
import sys, os, time, torch
import numpy as np, pandas as pd
import torch.nn.functional as F
from torch.utils.data import DataLoader

device = torch.device('cuda')
BATCH = 64
N_EPOCH = 300
N_INFER = 300


def measure(model, loader, is_drugban):
    model.train()
    opt = torch.optim.Adam(model.parameters())
    torch.cuda.reset_peak_memory_stats(device)
    t0 = time.time()
    it = iter(loader)
    for i in range(N_EPOCH):
        try:
            bg, prot, label = next(it)
        except StopIteration:
            it = iter(loader); bg, prot, label = next(it)
        bg, prot = bg.to(device), prot.to(device)
        label = label.float().to(device)
        if is_drugban:
            _, _, _, score = model(bg, prot, mode='train')
            loss = F.binary_cross_entropy_with_logits(score.squeeze(1), label)
        else:
            _, _, _, score = model(bg, prot, mode='train')
            loss = F.binary_cross_entropy(score.squeeze(1), label)
        opt.zero_grad(); loss.backward(); opt.step()
    ep_time = time.time() - t0
    peak = torch.cuda.max_memory_allocated(device) / 1e9
    model.eval()
    t0 = time.time()
    it = iter(loader); cnt = 0
    with torch.no_grad():
        for i in range(N_INFER):
            try:
                bg, prot, label = next(it)
            except StopIteration:
                it = iter(loader); bg, prot, label = next(it)
            bg, prot = bg.to(device), prot.to(device)
            if is_drugban:
                _, _, score, _ = model(bg, prot, mode='eval')
            else:
                _, _, score, _ = model(bg, prot, mode='eval')
            cnt += 1
    sps = cnt * BATCH / (time.time() - t0)
    return ep_time, peak, sps


# ---------- SGBANDTI full & no-subgraph ----------
from dataloader import DTIDataset as SGDD, collate_fn_nested
from models import SGBANDTI
from configs import get_cfg_defaults

df = pd.read_csv('datasets/biosnap/random/train.csv')
results = {}
for name, use_sub, use_nest in [('SGBANDTI', True, True), ('SGBANDTI-no-subgraph', False, False)]:
    cfg = get_cfg_defaults()
    cfg.ABLATION.USE_SUBGRAPH = use_sub
    model = SGBANDTI(**cfg).to(device)
    params = sum(p.numel() for p in model.parameters())
    ds = SGDD(df.index.values, df, dataset_name='biosnap', split_name='random', split_file_name='train',
              h=2, use_nested=use_nest, cache_root='./datasets/subgraph_cache')
    loader = DataLoader(ds, batch_size=BATCH, shuffle=False, num_workers=0, drop_last=True, collate_fn=collate_fn_nested)
    ep, mem, sps = measure(model, loader, is_drugban=False)
    results[name] = (params, ep, mem, sps)
    print(f'{name}: params={params} epoch={ep:.1f}s mem={mem:.2f}GB sps={sps:.0f}', flush=True)

# ---------- DrugBAN ----------
sys.path.insert(0, os.path.abspath('comprare/DrugBAN-main'))
import importlib.util
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

db_dataloader = load_mod('db_dataloader', 'comprare/DrugBAN-main/dataloader.py')
db_models = load_mod('db_models', 'comprare/DrugBAN-main/models.py')
db_configs = load_mod('db_configs', 'comprare/DrugBAN-main/configs.py')
db_utils = load_mod('db_utils', 'comprare/DrugBAN-main/utils.py')

db_cfg = db_configs.get_cfg_defaults()
model = db_models.DrugBAN(**db_cfg).to(device)
params = sum(p.numel() for p in model.parameters())
df_db = pd.read_csv('comprare/DrugBAN-main/datasets/biosnap/random/train.csv')
ds = db_dataloader.DTIDataset(df_db.index.values, df_db)
loader = DataLoader(ds, batch_size=BATCH, shuffle=False, num_workers=0, drop_last=True, collate_fn=db_utils.graph_collate_func)
ep, mem, sps = measure(model, loader, is_drugban=True)
results['DrugBAN'] = (params, ep, mem, sps)
print(f'DrugBAN: params={params} epoch={ep:.1f}s mem={mem:.2f}GB sps={sps:.0f}', flush=True)

print('\n=== SUMMARY ===')
for k, v in results.items():
    print(f'{k}: params={v[0]}  train_epoch={v[1]:.1f}s  peak_mem={v[2]:.2f}GB  infer={v[3]:.0f}samples/s', flush=True)
