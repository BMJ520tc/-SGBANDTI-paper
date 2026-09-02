from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 16,
        "axes.titlesize": 18,
        "axes.labelsize": 18,
        "xtick.labelsize": 15,
        "ytick.labelsize": 16,
        "legend.fontsize": 15,
        "axes.linewidth": 1.2,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }
)


OUTPUT_STEM = Path(__file__).resolve().parent / "figure_biosnap_split_boxplots"

# Per-seed AUROC/AUPRC (seeds 42, 52, 62, 72, 82).
# Random-split values come from the local per-seed results
# (result/biosnap_random_hop2/seed_summary_stats.csv); unseen-drug and
# unseen-target values come from the laboratory final summary
# (SGBANDTI__20260823/results/00_实验结果汇总.md).
scenarios = [
    {
        "label": "Random",
        "auroc": np.array([0.9062, 0.9090, 0.9040, 0.9065, 0.9052]),
        "auprc": np.array([0.9171, 0.9180, 0.9093, 0.9086, 0.9130]),
    },
    {
        "label": "Unseen drug",
        "auroc": np.array([0.8801, 0.8764, 0.8813, 0.8805, 0.8785]),
        "auprc": np.array([0.8820, 0.8824, 0.8861, 0.8803, 0.8795]),
    },
    {
        "label": "Unseen target",
        "auroc": np.array([0.6567, 0.6154, 0.6461, 0.6167, 0.6378]),
        "auprc": np.array([0.6282, 0.5861, 0.6355, 0.5953, 0.6170]),
    },
]


def sample_sd(x):
    return x.std(ddof=1)


def main() -> None:
    labels = [s["label"] for s in scenarios]
    x = np.arange(len(scenarios))

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.0), dpi=300, sharey=False)

    colors = ["#1f5aa6", "#2e8b57", "#c0392b"]
    for ax, metric, key in ((axes[0], "AUROC", "auroc"), (axes[1], "AUPRC", "auprc")):
        for i, s in enumerate(scenarios):
            vals = s[key]
            mean, sd = vals.mean(), sample_sd(vals)
            # Per-seed points with jitter along x to avoid overlap
            jitter = np.linspace(-0.15, 0.15, len(vals))
            ax.scatter(
                x[i] + jitter,
                vals,
                s=60,
                color=colors[i],
                alpha=0.85,
                edgecolor="white",
                linewidth=0.8,
                zorder=3,
                label=s["label"] if ax is axes[0] else None,
            )
            # Mean marker
            ax.plot(x[i], mean, marker="D", color=colors[i], markersize=8, zorder=4)
            # Error bar = sample SD (ddof=1)
            ax.errorbar(
                x[i],
                mean,
                yerr=sd,
                fmt="none",
                ecolor="black",
                elinewidth=1.6,
                capsize=6,
                capthick=1.6,
                zorder=2,
            )
            # Annotate mean +- sample SD above the error bar
            ax.text(
                x[i],
                mean + sd + 0.008,
                f"{mean:.4f}±{sd:.4f}",
                ha="center",
                va="bottom",
                fontsize=7,
                color="black",
            )
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel(metric)
        ax.set_ylim(0.56, 0.965) if metric == "AUPRC" else ax.set_ylim(0.58, 0.965)
        ax.grid(axis="y", color="#d9d9d9", linewidth=0.8, alpha=0.8, zorder=0)
        ax.tick_params(axis="both", direction="in", length=5, width=1.0, pad=6)

    axes[0].legend(loc="lower left", frameon=True, facecolor="white", edgecolor="#d0d0d0", framealpha=0.96)

    for ax in axes:
        for spine in ax.spines.values():
            spine.set_linewidth(1.2)

    fig.subplots_adjust(left=0.08, right=0.98, top=0.94, bottom=0.15, wspace=0.22)

    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUTPUT_STEM.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight")

    plt.close(fig)
    print("Figure regenerated at", OUTPUT_STEM)


if __name__ == "__main__":
    main()
