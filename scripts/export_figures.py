"""Export publication-independent PNG/SVG figures from a measured experiment."""

import json
import os
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".local" / "matplotlib")
)
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt  # noqa: E402


def main():
    root = Path(__file__).resolve().parents[1]
    run_id = json.loads((root / "runs" / "latest.json").read_text())["run_id"]
    report = json.loads((root / "runs" / run_id / "report.json").read_text(encoding="utf-8"))
    output = root / "reports" / "figures"
    output.mkdir(parents=True, exist_ok=True)
    selected = report["selected_model"]
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": "#1c302b",
            "text.color": "#1c302b",
            "savefig.dpi": 180,
        }
    )
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8), layout="constrained")
    for model, color, style in [
        (selected, "#24624b", "-"),
        ("gamma_poisson", "#976b38", "--"),
        ("recency", "#64786c", ":"),
    ]:
        weeks = report["final"][model]["weekly"]
        axes[0].plot(
            range(len(weeks)),
            [week["average_precision"] for week in weeks],
            linestyle=style,
            color=color,
            marker="o",
            markersize=3,
            label=report["model_names"][model],
        )
    axes[0].set(
        xlabel="Final holdout week (starting 5 September 2011)",
        ylabel="Average precision",
        ylim=(0, 0.5),
        title="Predictive ranking through time",
    )
    axes[0].legend(frameon=False, fontsize=9)
    bins = [record for record in report["final"][selected]["calibration"] if record["count"]]
    axes[1].plot([0, 1], [0, 1], color="#976b38", linestyle="--", label="Ideal agreement")
    axes[1].scatter(
        [b["predicted"] for b in bins],
        [b["observed"] for b in bins],
        s=[max(25, min(150, b["count"] / 100)) for b in bins],
        color="#24624b",
        label="Calibrated model",
    )
    axes[1].set(
        xlabel="Mean predicted purchase probability",
        ylabel="Observed purchase rate",
        xlim=(0, 1),
        ylim=(0, 1),
        title="Probability calibration",
    )
    axes[1].legend(frameon=False, fontsize=9)
    for axis in axes:
        axis.grid(axis="y", alpha=0.18)
        axis.set_axisbelow(True)
    figure.suptitle("ReorderIQ · Public retail benchmark, 13-week temporal holdout", fontsize=14)
    for extension in ["png", "svg"]:
        figure.savefig(output / f"model-evidence.{extension}")
    plt.close(figure)
    (output / "SOURCE.txt").write_text(
        f"Run: {run_id}\nUCI Online Retail II, Chen (2012), DOI:10.24432/C5CG6D, CC BY 4.0.\nObservational purchases, not outreach effects.\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
