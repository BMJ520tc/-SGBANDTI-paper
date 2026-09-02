# -*- coding: utf-8 -*-
"""公平纯前向时间对比: SGBANDTI(缓存子图) vs DrugBAN(复用已构建输入)。
分别报告纯模型前向(排除预处理/构图),DrugBAN 构图时间单独报。"""
import os, sys, time, torch
import numpy as np, pandas as pd
from torch.utils.data import DataLoader

device = torch.device('cuda')
BATCH = 64
N = 300

# ---------- SGBANDTI 纯前向(缓存子图,无构图) ----------
from dataloader import DTIDataset, collate_fn_nested
from models import SGBANDTI
from configs import get_cfg_defaults
model = SGBANDTI(**get_cfg_defaults()).to(device).eval()
df = pd.read_csv('datasets/biosnap/random/test.csv')
ds = DTIDataset(df.index.values, df, dataset_name='biosnap', split_name='random', split_file_name='test',
                h=2, use_nested=True, cache_root='./datasets/subgraph_cache')
loader = DataLoader(ds, batch_size=BATCH, shuffle=False, num_workers=0, collate_fn=collate_fn_nested)
it = iter(loader); bg, prot, _ = next(it); bg, prot = bg.to(device), prot.to(device)
with torch.no_grad(): model(bg, prot, mode='eval')
t0 = time.time()
with torch.no_grad():
    for i in range(N):
        try: bg, prot, _ = next(it)
        except StopIteration: it = iter(loader); bg, prot, _ = next(it)
        bg, prot = bg.to(device), prot.to(device)
        model(bg, prot, mode='eval')
sgb_sps = N * BATCH / (time.time() - t0)
print(f'SGBANDTI 纯前向(缓存子图): {sgb_sps:.0f} samples/s')

# ---------- DrugBAN 纯前向(复用已构建 batch;构图时间单独) ----------
sys.path.insert(0, os.path.abspath('comprare/DrugBAN-main'))
import importlib.util
def load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s); sys.modules[n] = m
    s.loader.exec_module(m); return m
db_dl = load('db_dl2', 'comprare/DrugBAN-main/dataloader.py')
db_md = load('db_md2', 'comprare/DrugBAN-main/models.py')
db_cfg = load('db_cfg2', 'comprare/DrugBAN-main/configs.py')
db_ut = load('db_ut2', 'comprare/DrugBAN-main/utils.py')
cfg = db_cfg.get_cfg_defaults()
model = db_md.DrugBAN(**cfg).to(device).eval()
df = pd.read_csv('comprare/DrugBAN-main/datasets/biosnap/random/test.csv')
dls = db_dl.DTIDataset(df.index.values, df)
loader = DataLoader(dls, batch_size=BATCH, shuffle=False, num_workers=0, collate_fn=db_ut.graph_collate_func)
# 构图(构建一个 batch)耗时
t0 = time.time(); bg, prot, _ = next(iter(loader)); t_graph = time.time() - t0
bg, prot = bg.to(device), prot.to(device)
saved_h = bg.ndata['h'].clone()  # 保存 h(预热 forward 会 pop 它)
with torch.no_grad(): model(bg, prot, mode='eval')
# 纯前向(复用同一输入; DrugBAN GCN 会 pop ndata['h'], 每轮前向重新赋值)
t0 = time.time()
with torch.no_grad():
    for i in range(N):
        bg.ndata['h'] = saved_h
        model(bg, prot, mode='eval')
db_sps = N * BATCH / (time.time() - t0)
print(f'DrugBAN 纯前向(复用输入,无构图): {db_sps:.0f} samples/s; 构图 {t_graph*1000:.0f} ms/batch({BATCH})')
