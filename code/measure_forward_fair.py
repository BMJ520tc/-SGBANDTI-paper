# -*- coding: utf-8 -*-
"""公平纯前向时间对比: SGBANDTI(缓存子图) vs DrugBAN(复用已构建输入)。
分别报告纯模型前向(排除预处理/构图);DrugBAN 构图时间单独报。
在 code/ 目录内运行(仓库根/code)。计时含 torch.cuda.synchronize、预热与重复取均值。"""
import os, sys, time, torch
import numpy as np, pandas as pd
from torch.utils.data import DataLoader

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA = os.path.join(ROOT, 'data')
DBAN = os.path.join(ROOT, 'baselines', 'DrugBAN')
device = torch.device('cuda')
BATCH = 64
N = 100
REPEAT = 3
REPS = 10  # 每个 seed 内部重复取均值的次数


def timed_forward(fn, reps=REPS):
    """预热后计时 reps 轮,返回 (samples_per_s, 每批耗时s)。"""
    # 预热
    torch.cuda.synchronize()
    for _ in range(5):
        fn()
    torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        fn()
        torch.cuda.synchronize()
        ts.append(time.perf_counter() - t0)
    ts = np.array(ts)
    return BATCH / ts.mean(), ts.mean()


# ---------- SGBANDTI 纯前向(缓存子图,无构图) ----------
sys.path.insert(0, os.path.dirname(__file__))
from dataloader import DTIDataset, collate_fn_nested  # noqa: E402
from models import SGBANDTI  # noqa: E402
from configs import get_cfg_defaults  # noqa: E402

model = SGBANDTI(**get_cfg_defaults()).to(device).eval()
df = pd.read_csv(os.path.join(DATA, 'biosnap/random/test.csv'))
ds = DTIDataset(df.index.values, df, dataset_name='biosnap', split_name='random',
                split_file_name='test', h=2, use_nested=True,
                cache_root=os.path.join(DATA, 'subgraph_cache'))
loader = DataLoader(ds, batch_size=BATCH, shuffle=False, num_workers=0,
                    collate_fn=collate_fn_nested)
it = iter(loader)
bg, prot, _ = next(it)
bg, prot = bg.to(device), prot.to(device)
sgb_sps, sgb_batch_t = timed_forward(lambda: model(bg, prot, mode='eval'))
print(f'SGBANDTI 纯前向(缓存子图): {sgb_sps:.0f} samples/s ({sgb_batch_t*1000:.1f} ms/batch)')

# ---------- DrugBAN 纯前向(复用已构建 batch;构图时间单独) ----------
sys.path.insert(0, DBAN)
import importlib.util  # noqa: E402


def load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    sys.modules[n] = m
    s.loader.exec_module(m)
    return m


db_dl = load('db_dl2', os.path.join(DBAN, 'dataloader.py'))
db_md = load('db_md2', os.path.join(DBAN, 'models.py'))
db_cfg = load('db_cfg2', os.path.join(DBAN, 'configs.py'))
db_ut = load('db_ut2', os.path.join(DBAN, 'utils.py'))
cfg = db_cfg.get_cfg_defaults()
model = db_md.DrugBAN(**cfg).to(device).eval()
df = pd.read_csv(os.path.join(DATA, 'biosnap/random/test.csv'))
dls = db_dl.DTIDataset(df.index.values, df)
loader = DataLoader(dls, batch_size=BATCH, shuffle=False, num_workers=0,
                    collate_fn=db_ut.graph_collate_func)

# 构图(构建一个 batch)耗时 —— 单独、预热、重复
torch.cuda.synchronize()
for _ in range(5):
    next(iter(loader))
torch.cuda.synchronize()
t0 = time.perf_counter()
bg, prot, _ = next(iter(loader))
torch.cuda.synchronize()
t_graph = time.perf_counter() - t0
bg, prot = bg.to(device), prot.to(device)

saved_h = bg.ndata['h'].clone()  # 保存 h(预热 forward 会 pop 它)
with torch.no_grad():
    model(bg, prot, mode='eval')


def db_fwd():
    with torch.no_grad():
        bg.ndata['h'] = saved_h
        model(bg, prot, mode='eval')


db_sps, db_batch_t = timed_forward(db_fwd)
print(f'DrugBAN 纯前向(复用输入,无构图): {db_sps:.0f} samples/s ({db_batch_t*1000:.1f} ms/batch)')
print(f'DrugBAN 构图: {t_graph*1000:.0f} ms/batch({BATCH})')
