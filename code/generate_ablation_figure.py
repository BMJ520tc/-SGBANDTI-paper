from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 16,
        "axes.titlesize": 20,
        "axes.labelsize": 18,
        "xtick.labelsize": 15,
        "ytick.labelsize": 16,
        "legend.fontsize": 15,
        "axes.linewidth": 1.2,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }
)


OUTPUT_STEM = Path(__file__).resolve().parent / "figure_ablation_2x2"


def main() -> None:
    configs = ["Full\nSGBANDTI", "No\nsubgraph", "GCN\ntokens", "No\nBAN", "No\nboth"]
    auroc = np.array([0.9062, 0.8757, 0.9051, 0.8777, 0.8598])
    auprc = np.array([0.9132, 0.8782, 0.9110, 0.8759, 0.8551])

    # Sample SD (ddof=1) across five seeds (from result_metrics.pt).
    auroc_err = np.array([0.0019, 0.0014, 0.0043, 0.0025, 0.0028])
    auprc_err = np.array([0.0043, 0.0034, 0.0068, 0.0036, 0.0037])

    bar_blue = "#1f5aa6"
    bar_slate = "#7d89b8"
    grid_color = "#d9d9d9"

    fig, ax1 = plt.subplots(figsize=(7.6, 5.4), dpi=300)

    x = np.arange(len(configs))
    width = 0.35

    bars1 = ax1.bar(
        x - width / 2,
        auroc,
        width=width,
        color=bar_blue,
        edgecolor="white",
        linewidth=1.1,
        yerr=auroc_err,
        capsize=5.0,
        ecolor="black",
        error_kw={"elinewidth": 1.8, "capthick": 1.8},
        label="AUROC",
        zorder=3,
    )
    bars2 = ax1.bar(
        x + width / 2,
        auprc,
        width=width,
        color=bar_slate,
        edgecolor="white",
        linewidth=1.1,
        yerr=auprc_err,
        capsize=5.0,
        ecolor="black",
        error_kw={"elinewidth": 1.8, "capthick": 1.8},
        label="AUPRC",
        zorder=3,
    )

    ax1.set_title("Full model, replacement configurations, and GCN-token control", pad=14)
    ax1.set_ylabel("Score")
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs)
    ax1.set_ylim(0.84, 0.925)
    ax1.set_yticks(np.arange(0.84, 0.926, 0.01))
    ax1.grid(axis="y", color=grid_color, linewidth=1.0, alpha=0.9, zorder=0)
    ax1.tick_params(axis="both", direction="in", length=5.5, width=1.0, pad=6)
    ax1.legend(
        handles=[bars1, bars2],
        labels=["AUROC", "AUPRC"],
        loc="upper right",
        bbox_to_anchor=(0.98, 0.98),
        frameon=True,
        facecolor="white",
        edgecolor="#d0d0d0",
        framealpha=0.96,
        borderpad=0.5,
    )

    for spine in ax1.spines.values():
        spine.set_linewidth(1.2)

    fig.subplots_adjust(left=0.10, right=0.985, top=0.88, bottom=0.17)

    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUTPUT_STEM.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight")

    plt.close(fig)


if __name__ == "__main__":
    main()
