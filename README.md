# rebound-viz — N-body Trajectory Viewer

[English](#english) | [日本語](#日本語)

---

## English

A small pipeline that integrates gravitational **N-body systems with [REBOUND](https://rebound.readthedocs.io/)** and renders the trajectories in a Three.js viewer in the browser.

### Run
```sh
cd ~/dev/rebound-viz
python3 -m venv venv && ./venv/bin/pip install rebound numpy
./venv/bin/python simulate.py                    # default: perturbed 3-body chaos
./venv/bin/python simulate.py --system cluster --n 40
./venv/bin/python simulate.py --system figure8 --tmax 20
# then open viewer.html (e.g. python3 -m http.server)
```

### Systems
- `figure8` — the stable Chenciner–Montgomery figure-eight orbit (not chaotic, but beautiful).
- `chaos3` — the figure-eight slightly perturbed into 3-body chaos (default).
- `cluster` — an N-body mini star cluster that gravitationally gathers and scatters.

### Files
- `simulate.py` — integrates the system and exports position samples to `traj_*.json`.
- `viewer.html` — Three.js viewer that reads the trajectory JSON directly.
- `traj_figure8.json` / `traj_chaos3.json` / `traj_cluster.json` — precomputed trajectories.

> `venv/` is git-ignored.

---

## 日本語

重力**多体系を [REBOUND](https://rebound.readthedocs.io/) で積分**し、軌跡をブラウザの Three.js
ビューアで表示する小さなパイプライン。

### 実行
```sh
cd ~/dev/rebound-viz
python3 -m venv venv && ./venv/bin/pip install rebound numpy
./venv/bin/python simulate.py                    # デフォルト: 摂動を加えた三体カオス
./venv/bin/python simulate.py --system cluster --n 40
./venv/bin/python simulate.py --system figure8 --tmax 20
# その後 viewer.html を開く（例: python3 -m http.server）
```

### 系
- `figure8` — 安定な Chenciner–Montgomery の8の字解（カオスではないが美しい）。
- `chaos3` — 8の字をわずかに摂動した三体カオス（デフォルト）。
- `cluster` — 重力で集まりつつ散る N 体の小星団。

### ファイル
- `simulate.py` — 系を積分し、位置サンプルを `traj_*.json` に書き出す。
- `viewer.html` — 軌跡 JSON をそのまま読む Three.js ビューア。
- `traj_figure8.json` / `traj_chaos3.json` / `traj_cluster.json` — 計算済み軌跡。

> `venv/` は git 管理外。
