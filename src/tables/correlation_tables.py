import pandas as pd


def pearsonr_table(r1, r2, p1, p2):

    # format small p-values
    fmt_p = lambda p: "< 0.001" if p < 0.001 else f"{p:.4f}"

    # Build metrics table
    metrics_df = pd.DataFrame({
        "Schedule Metric": [
            "Bedtime vs. Sleep Length",
            "Bedtime vs. Wake Time (Sleeping In)",
        ],
        "Correlation (r)": [
            f"{r1:+.3f}",
            f"{r2:+.3f}",
        ],
        "R² (Variance)": [
            f"{r1**2:.3f} ({r1**2 * 100:.1f}%)",
            f"{r2**2:.3f} ({r2**2 * 100:.1f}%)",
        ],
        "p-value": [fmt_p(p1), fmt_p(p2)],
    })

    styler = metrics_df.style.hide(axis="index").set_properties(**
    {
    "padding": "6px",
    "border": "1px solid black"
        })


    return styler