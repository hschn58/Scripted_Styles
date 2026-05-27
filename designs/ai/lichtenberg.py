import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")

# --- Parameters ---
WIDTH, HEIGHT = 800, 800
ETA = 2.5
LAPLACE_ITERS = 20
FILL_FRACTION = 0.04
SEED_MODE = "center"
NUM_SEEDS = 1
GRAIN_OCTAVES = 5
GRAIN_STRENGTH = 0.85
COLORMAP = "inferno"
DPI = 600
OUTPUT = "lichtenberg.png"


def fractal_noise(h, w, octaves, rng):
    result = np.zeros((h, w), dtype=np.float64)
    for o in range(octaves):
        freq = 2 ** (o + 2)
        amp = 1.0 / (o + 1)
        gy = np.linspace(0, freq, h, endpoint=False)
        gx = np.linspace(0, freq, w, endpoint=False)
        iy0 = gy.astype(int) % freq
        ix0 = gx.astype(int) % freq
        iy1 = (iy0 + 1) % freq
        ix1 = (ix0 + 1) % freq
        fy = (gy - np.floor(gy))[:, None]
        fx = (gx - np.floor(gx))[None, :]
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        lattice = rng.standard_normal((freq, freq))
        v00 = lattice[iy0][:, ix0]
        v10 = lattice[iy1][:, ix0]
        v01 = lattice[iy0][:, ix1]
        v11 = lattice[iy1][:, ix1]
        interp = v00 * (1 - fy) * (1 - fx) + v10 * fy * (1 - fx) + v01 * (1 - fy) * fx + v11 * fy * fx
        result += amp * interp
    lo, hi = result.min(), result.max()
    return (result - lo) / (hi - lo)


def make_dielectric(h, w, octaves, strength, rng):
    noise = fractal_noise(h, w, octaves, rng)
    grain = np.sin(noise * 12 * np.pi + np.linspace(0, 6 * np.pi, w)[None, :])
    grain = (grain + 1) / 2
    dielectric = 1.0 - strength * grain
    return np.clip(dielectric, 0.05, 1.0)


def init_seeds(w, h, mode, n, rng):
    if mode == "center":
        return [(w // 2, h // 2)]
    if mode == "edge":
        return [(w // 2, 0)]
    return [(rng.integers(0, w), rng.integers(0, h)) for _ in range(n)]


def solve_laplace(phi, frozen, boundary_mask, iters):
    for _ in range(iters):
        phi[1:-1, 1:-1] = 0.25 * (
            phi[:-2, 1:-1] + phi[2:, 1:-1] +
            phi[1:-1, :-2] + phi[1:-1, 2:]
        )
        phi[frozen] = 0.0
        phi[boundary_mask] = 1.0
        phi[0, :] = phi[1, :]
        phi[-1, :] = phi[-2, :]
        phi[:, 0] = phi[:, 1]
        phi[:, -1] = phi[:, -2]


def get_candidates_8(frozen, growable):
    adj = np.zeros_like(frozen)
    adj[1:, :] |= frozen[:-1, :]
    adj[:-1, :] |= frozen[1:, :]
    adj[:, 1:] |= frozen[:, :-1]
    adj[:, :-1] |= frozen[:, 1:]
    adj[1:, 1:] |= frozen[:-1, :-1]
    adj[1:, :-1] |= frozen[:-1, 1:]
    adj[:-1, 1:] |= frozen[1:, :-1]
    adj[:-1, :-1] |= frozen[1:, 1:]
    return np.argwhere(adj & ~frozen & growable)


def compute_gradient(phi, candidates):
    cy, cx = candidates[:, 0], candidates[:, 1]
    h, w = phi.shape
    gy = phi[np.clip(cy + 1, 0, h - 1), cx] - phi[np.clip(cy - 1, 0, h - 1), cx]
    gx = phi[cy, np.clip(cx + 1, 0, w - 1)] - phi[cy, np.clip(cx - 1, 0, w - 1)]
    return np.sqrt(gx * gx + gy * gy)


def grow(w, h, eta, fill_frac, laplace_iters, seed_mode, num_seeds,
         dielectric, rng_seed=42):
    rng = np.random.default_rng(rng_seed)

    frozen = np.zeros((h, w), dtype=bool)
    order = np.full((h, w), -1, dtype=np.int32)
    step = 0

    seeds = init_seeds(w, h, seed_mode, num_seeds, rng)
    cy_seed = int(np.mean([s[1] for s in seeds]))
    cx_seed = int(np.mean([s[0] for s in seeds]))

    for sx, sy in seeds:
        frozen[sy, sx] = True
        order[sy, sx] = step
        step += 1

    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((Y - cy_seed) ** 2 + (X - cx_seed) ** 2)
    max_r = min(cy_seed, cx_seed, h - 1 - cy_seed, w - 1 - cx_seed)
    boundary_r = int(max_r * 0.92)
    boundary_mask = (dist >= boundary_r) & (dist < boundary_r + 3)
    growable = dist < (boundary_r - 6)
    display_r = boundary_r - 8

    phi = np.zeros((h, w), dtype=np.float64)
    phi[boundary_mask] = 1.0
    phi[growable & ~frozen] = 0.5

    target = int(fill_frac * w * h)
    # Warm-start: first solve gets more iterations to establish the field
    solve_laplace(phi, frozen, boundary_mask, laplace_iters * 10)

    while step < target:
        # Warm-start: only a few iterations since phi is nearly correct from last step
        solve_laplace(phi, frozen, boundary_mask, laplace_iters)

        candidates = get_candidates_8(frozen, growable)
        if len(candidates) == 0:
            break

        grad = compute_gradient(phi, candidates)
        cy, cx = candidates[:, 0], candidates[:, 1]
        probs = (grad * dielectric[cy, cx]) ** eta

        total = probs.sum()
        if total == 0:
            probs = np.ones_like(probs)
            total = probs.sum()
        probs /= total

        idx = rng.choice(len(candidates), p=probs)
        y, x = candidates[idx]
        frozen[y, x] = True
        phi[y, x] = 0.0
        order[y, x] = step
        step += 1

        if step % 1000 == 0:
            pct = step / (w * h) * 100
            print(f"  {step:>6d} pixels ({pct:.1f}%)")

    return order, frozen, dist, display_r


def render(order, frozen, dist, display_r, cmap, dpi, output):
    visible = frozen & (dist < display_r)
    masked = np.ma.masked_where(~visible, order.astype(float))
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(masked, cmap=cmap, interpolation="nearest")
    ax.set_axis_off()
    fig.patch.set_facecolor("black")
    fig.savefig(output, dpi=dpi, bbox_inches="tight",
                facecolor="black", pad_inches=0)
    plt.close(fig)
    print(f"Saved {output} at {dpi} DPI")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lichtenberg figures via Dielectric Breakdown Model")
    parser.add_argument("--width", type=int, default=WIDTH)
    parser.add_argument("--height", type=int, default=HEIGHT)
    parser.add_argument("--eta", type=float, default=ETA)
    parser.add_argument("--fill", type=float, default=FILL_FRACTION)
    parser.add_argument("--laplace-iters", type=int, default=LAPLACE_ITERS)
    parser.add_argument("--seed-mode", choices=["center", "edge", "random"], default=SEED_MODE)
    parser.add_argument("--num-seeds", type=int, default=NUM_SEEDS)
    parser.add_argument("--grain-octaves", type=int, default=GRAIN_OCTAVES)
    parser.add_argument("--grain-strength", type=float, default=GRAIN_STRENGTH)
    parser.add_argument("--cmap", default=COLORMAP)
    parser.add_argument("--dpi", type=int, default=DPI)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("--rng-seed", type=int, default=42)
    args = parser.parse_args()

    rng = np.random.default_rng(args.rng_seed)
    dielectric = make_dielectric(args.height, args.width, args.grain_octaves,
                                 args.grain_strength, rng)

    print(f"Growing: {args.width}x{args.height}, eta={args.eta}, fill={args.fill*100:.0f}%, "
          f"grain_strength={args.grain_strength}")
    order, frozen, dist, display_r = grow(
        args.width, args.height, args.eta, args.fill,
        args.laplace_iters, args.seed_mode, args.num_seeds,
        dielectric, args.rng_seed,
    )
    render(order, frozen, dist, display_r, args.cmap, args.dpi, args.output)
