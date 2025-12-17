import numpy as np
import matplotlib.pyplot as plt
import ehtim as eh

# one_freqの情報
# tag = "one_freq"
# uvfile = "one_freq"
# uvfile = "rec_one_freq"

# two_freqの情報
# tag = "two_freq"
# uvfile = "fpt_two_freq"
# uvfile = "two_freq"

# spaceの情報
tag = "space"
uvfile = "space"
# uvfile = "fpt_space"

obs = eh.obsdata.load_uvfits("./" + tag + "/" + uvfile + ".uvfits")
obs = obs.switch_polrep(polrep_out="stokes")
# 観測データ
dat = obs.unpack(["u", "v", "snr"])
u_all = dat["u"] / 1e9  # Gλ
v_all = dat["v"] / 1e9
snr = dat["snr"]


# uv 長さ r = sqrt(u^2 + v^2)
r = np.sqrt(u_all**2 + v_all**2)
print(np.unique(obs.unpack("t1")["t1"]))
print(np.unique(obs.unpack("t2")["t2"]))
short_mask = r <= 1.0  # short baselines (≤ 1 Gλ)
long_mask = r > 1.0  # long  baselines (> 1 Gλ)

# ---- SNR ビンの定義 ----
snr_edges = [1, 10, 100, 1000, 1e9]  # 上限は適当に大きく
snr_labels = ["1–10", "10–100", "100–1000", "≥1000"]
snr_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]


# 軸範囲を共通にして見やすく
lim = np.max(np.abs(np.concatenate([u_all, v_all])))
lim = 1.05 * lim

fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# ================= Short baselines ==================
ax = axes[0]

# 各 SNR ビンごとに色を変えて描画
for low, high, label, color in zip(
    snr_edges[:-1], snr_edges[1:], snr_labels, snr_colors
):
    msk = short_mask & (snr >= low) & (snr < high)
    if np.any(msk):
        ax.scatter(
            u_all[msk] * 1000,
            v_all[msk] * 1000,
            s=10,
            alpha=0.8,
            color=color,
            label=label,
        )
        ax.scatter(-u_all[msk] * 1000, -v_all[msk] * 1000, s=10, alpha=0.4, color=color)

ax.set_title("Short baselines (r ≤ 1 Gλ)")
ax.set_xlabel("u [Mλ]")
ax.set_ylabel("v [Mλ]")
ax.set_aspect("equal", adjustable="box")
ax.grid(alpha=0.2)

# ================= Long baselines ==================
ax = axes[1]

# SNR ビンごと
for low, high, label, color in zip(
    snr_edges[:-1], snr_edges[1:], snr_labels, snr_colors
):
    msk = long_mask & (snr >= low) & (snr < high)
    if np.any(msk):
        ax.scatter(u_all[msk], v_all[msk], s=10, alpha=0.8, color=color, label=label)
        ax.scatter(-u_all[msk], -v_all[msk], s=10, alpha=0.4, color=color)

ax.set_title("Long baselines (r > 1 Gλ)")
ax.set_xlabel("u [Gλ]")
ax.set_ylabel("v [Gλ]")
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.grid(alpha=0.2)

# ---- SNR ビンの凡例を図外にまとめて表示 ----
from matplotlib.patches import Patch

handles = [Patch(color=c, label=lab) for c, lab in zip(snr_colors, snr_labels)]

fig.subplots_adjust(right=0.80)
fig.legend(
    handles,
    snr_labels,
    loc="center right",
    bbox_to_anchor=(0.97, 0.5),
    title="SNR",
    fontsize=10,
)

plt.tight_layout(rect=[0, 0, 0.80, 1])

plt.savefig("./" + tag + "/" + uvfile + "_uv_baselines.pdf")

#####################
# ---- extract needed data ----
dat = obs.unpack(["u", "v", "amp", "snr"])
u_all = dat["u"] / 1e9  # convert to Gλ
v_all = dat["v"] / 1e9
amp = dat["amp"]
snr = dat["snr"]

# ---- compute uv-distance ----
r = np.sqrt(u_all**2 + v_all**2)  # Gλ baseline length

# ---- define SNR bins for coloring ----
snr_edges = [1, 10, 100, 1000, 1e9]
snr_labels = ["1–10", "10–100", "100–1000", "≥1000"]
snr_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

low_snr_mask = snr < 1.0  # below detection threshold

# ---- create plot ----
plt.figure(figsize=(10, 7))

# plot low SNR first in gray
msk = low_snr_mask
plt.scatter(r[msk], amp[msk], s=8, alpha=0.3, color="lightgray", label="<1")

# loop through bins and plot points
for low, high, label, color in zip(
    snr_edges[:-1], snr_edges[1:], snr_labels, snr_colors
):
    msk = (snr >= low) & (snr < high)
    if np.any(msk):
        plt.scatter(r[msk], amp[msk], s=15, alpha=0.8, color=color, label=label)

# ---- axes format ----
plt.xlabel("uv-distance [Gλ]")
plt.ylabel("Visibility Amplitude[Jy]")
plt.title("uv-distance vs Amplitude (Colored by SNR)")
plt.grid(alpha=0.2)

# ---- log-scaling option for amplitude ----
plt.yscale("log")  # comment out if linear needed

# ---- add legend ----
from matplotlib.patches import Patch

handles = [
    Patch(color=c, label=lab)
    for c, lab in zip(["lightgray"] + snr_colors, ["<1"] + snr_labels)
]

plt.legend(handles, [h.get_label() for h in handles], title="SNR", fontsize=10)

plt.tight_layout()
plt.savefig("./" + tag + "/" + uvfile + "_uv_amp.pdf")
