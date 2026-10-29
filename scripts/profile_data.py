"""Descriptive source profile, separate from model fitting or tuning."""

import json
from pathlib import Path

import pandas as pd


def main():
    root = Path(__file__).resolve().parents[1]
    orders = pd.read_parquet(root / "data" / "processed" / "orders.parquet")
    audit = json.loads((root / "data" / "processed" / "audit.json").read_text())
    counts = orders.groupby("customer_id").size()
    monthly = orders.groupby(orders.ordered_at.dt.strftime("%Y-%m")).size()
    profile = {
        "orders": len(orders),
        "buyers": int(counts.size),
        "single_observed_order_buyers": int((counts == 1).sum()),
        "median_observed_orders_per_buyer": float(counts.median()),
        "orders_per_buyer_p95": float(counts.quantile(0.95)),
        "median_basket_gbp": float(orders.amount_gbp.median()),
        "basket_gbp_p99": float(orders.amount_gbp.quantile(0.99)),
        "monthly_orders": {key: int(value) for key, value in monthly.items()},
        "missing_customer_lines_excluded": audit["exclusions"]["invalid_customer"],
        "source_lines": audit["raw_lines"],
    }
    output = root / "reports"
    output.mkdir(exist_ok=True)
    (output / "data-profile.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Descriptive source profile",
        "",
        "Computed from accepted invoice-level orders; not used to tune final models.",
        "",
        f"- Observed orders: {profile['orders']:,}; buyers: {profile['buyers']:,}.",
        f"- Buyers with only one observed order: {profile['single_observed_order_buyers']:,}. This is not a known churn count.",
        f"- Median / 95th percentile observed orders per buyer: {profile['median_observed_orders_per_buyer']:.1f} / {profile['orders_per_buyer_p95']:.1f}.",
        f"- Median / 99th percentile accepted basket value: GBP {profile['median_basket_gbp']:.2f} / {profile['basket_gbp_p99']:.2f}.",
        f"- Excluded missing/invalid customer-ID lines: {profile['missing_customer_lines_excluded']:,} of {profile['source_lines']:,} raw lines. This changes population coverage.",
        "",
        "## Orders by source month",
        "",
        "| Month | Orders |",
        "|---|---:|",
    ]
    lines.extend(f"| {month} | {count:,} |" for month, count in profile["monthly_orders"].items())
    lines.extend(
        [
            "",
            "December 2011 is a partial month. Counts reflect this retailer and source coverage, not market-wide demand. Buyer histories are left/right truncated; the one-order count cannot establish permanent churn. Basket values are positive merchandise sums, not net revenue after returns.",
            "",
            "Source: Chen, D. (2012), UCI Online Retail II, DOI:10.24432/C5CG6D, CC BY 4.0.",
            "",
        ]
    )
    (output / "DATA_PROFILE.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
