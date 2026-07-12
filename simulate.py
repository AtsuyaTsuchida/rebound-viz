#!/usr/bin/env python
"""
REBOUND -> Three.js viewer 用の軌跡エクスポータ。

カオス多体系を積分し、各天体の位置サンプルを JSON に書き出す。
出力は trajectories.json で、viewer.html がそのまま読む。

使い方:
    ./venv/bin/python simulate.py                 # デフォルト: 三体カオス
    ./venv/bin/python simulate.py --system cluster --n 40
    ./venv/bin/python simulate.py --system figure8 --tmax 20

system:
    figure8  -- 安定な8の字解（カオスではないが美しい）
    chaos3   -- 8の字をわずかに摂動した三体カオス（デフォルト）
    cluster  -- N体の小星団。重力で集まりつつ散る
"""
import argparse
import json
import math
import numpy as np
import rebound


def make_figure8(sim):
    """Chenciner-Montgomery の 8 の字解。3 体が同一軌道を追う。"""
    # 規格化された初期条件（G=m=1）
    x1, y1 = 0.97000436, -0.24308753
    vx3, vy3 = -0.93240737, -0.86473146
    sim.add(m=1.0, x=x1,  y=y1,  z=0.0, vx=-vx3/2, vy=-vy3/2, vz=0.0)
    sim.add(m=1.0, x=-x1, y=-y1, z=0.0, vx=-vx3/2, vy=-vy3/2, vz=0.0)
    sim.add(m=1.0, x=0.0, y=0.0, z=0.0, vx=vx3,    vy=vy3,    vz=0.0)


def make_chaos3(sim, eps=1e-2):
    """8 の字をわずかに摂動 -> 鋭敏なカオス。"""
    make_figure8(sim)
    # 3 体目の速度に微小摂動を与えるとリアプノフ発散する
    sim.particles[2].vy += eps
    # 完全な平面運動だと退屈なので z 方向にも微小な揺らぎ
    sim.particles[0].vz += eps * 0.5
    sim.particles[1].vz -= eps * 0.5


def make_cluster(sim, n=40, seed=42):
    """小さな星団。Plummer 風の分布から初期配置。"""
    rng = np.random.default_rng(seed)
    for _ in range(n):
        # Plummer 球からサンプル
        r = 1.0 / math.sqrt(rng.uniform(0, 1) ** (-2.0 / 3.0) - 1.0)
        r = min(r, 5.0)
        theta = math.acos(rng.uniform(-1, 1))
        phi = rng.uniform(0, 2 * math.pi)
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        # ゆるい接線速度 + ランダム成分でゆっくり崩壊/膨張
        v = 0.3 * math.sqrt(1.0 / (r + 0.3))
        vx = -v * math.sin(phi) + rng.normal(0, 0.05)
        vy = v * math.cos(phi) + rng.normal(0, 0.05)
        vz = rng.normal(0, 0.05)
        m = rng.uniform(0.5, 2.0) / n
        sim.add(m=m, x=x, y=y, z=z, vx=vx, vy=vy, vz=vz)


def build_sim(system, n):
    sim = rebound.Simulation()
    sim.G = 1.0
    # NOTE: このビルド(rebound 5.0.0 / Py3.14)では IAS15 が integrate で
    # ハングする。WHFast は中心星を仮定する Kepler 分割なので等質量・中心星
    # なしの系では発散する。汎用 N 体に効く固定ステップの leapfrog を使う。
    sim.integrator = "leapfrog"
    if system == "figure8":
        make_figure8(sim)
        sim.dt = 1e-3
    elif system == "chaos3":
        make_chaos3(sim)
        sim.dt = 1e-3
    elif system == "cluster":
        make_cluster(sim, n=n)
        sim.dt = 2e-3
        sim.softening = 0.05              # 近接時の数値発散を抑える
    else:
        raise ValueError(f"unknown system: {system}")
    sim.move_to_com()                     # 重心を原点に固定（描画が安定）
    return sim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", default="chaos3",
                    choices=["figure8", "chaos3", "cluster"])
    ap.add_argument("--n", type=int, default=40, help="cluster の天体数")
    ap.add_argument("--tmax", type=float, default=12.0, help="積分する時間")
    ap.add_argument("--frames", type=int, default=1500, help="サンプル数")
    ap.add_argument("--out", default=None, help="出力名（既定: traj_<system>.json）")
    ap.add_argument("--all", action="store_true", help="全3系を一括生成")
    args = ap.parse_args()

    if args.all:
        for s in ("figure8", "chaos3", "cluster"):
            run(s, args.n, args.tmax, args.frames, f"traj_{s}.json")
        return
    out = args.out or f"traj_{args.system}.json"
    run(args.system, args.n, args.tmax, args.frames, out)


def run(system, n, tmax, frames, out):
    sim = build_sim(system, n)
    nbody = sim.N

    times = np.linspace(0, tmax, frames)
    # positions[frame][body] = [x, y, z]
    positions = np.zeros((frames, nbody, 3), dtype=np.float32)
    masses = [p.m for p in sim.particles]

    for i, t in enumerate(times):
        sim.integrate(t, exact_finish_time=0)   # 固定ステップで素直に進める
        for j, p in enumerate(sim.particles):
            positions[i, j] = (p.x, p.y, p.z)

    # 描画スケール用に座標の広がりを測る
    span = float(np.percentile(np.abs(positions), 98)) or 1.0

    data = {
        "system": system,
        "nbody": nbody,
        "frames": frames,
        "tmax": tmax,
        "span": span,
        "masses": masses,
        # frame-major のフラット配列（JSでTypedArray化しやすい）
        "positions": positions.reshape(-1).round(4).tolist(),
    }
    with open(out, "w") as f:
        json.dump(data, f)
    print(f"wrote {out}: system={system} bodies={nbody} "
          f"frames={frames} span={span:.3f}")


if __name__ == "__main__":
    main()
