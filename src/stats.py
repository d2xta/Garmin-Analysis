import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm



def get_summary(
    df: pd.DataFrame, metrics: list[str], decimals: int = 2
) -> pd.DataFrame:
    """Generate a clean summary table for multiple numeric metrics in a DataFrame.

    Parameters:
        df (pd.DataFrame): The source DataFrame containing the metrics.
        metrics (list[str]): List of numeric column names to summarize.
        decimals (int): Number of decimal places to round output strings to.

    Returns:
        pd.DataFrame: Summary table with one row per metric.
    """
    rows = []

    for metric in metrics:
        if metric not in df.columns:
            continue

        data = df[metric].dropna()

        if data.empty:
            continue

        # Pre-compute metrics to avoid redundant calls
        avg = data.mean()
        med = data.median()
        std = data.std()
        p10 = data.quantile(0.10)
        p90 = data.quantile(0.90)
        min_val = data.min()
        max_val = data.max()

        summary = {
            "Metric": metric,
            "Total Tracked": len(data),
            "Average": f"{avg:.{decimals}f}",
            "Typical (Median)": f"{med:.{decimals}f}",
            "Consistency (Std Dev)": f"{std:.{decimals}f}",
            "Core Range (80%)": f"{p10:.{decimals}f} to {p90:.{decimals}f}",
            "P10": f"{p10:.{decimals}f}",
            "P90": f"{p90:.{decimals}f}",
            "Absolute Range": f"{min_val:.{decimals}f} to {max_val:.{decimals}f}",
        }

        rows.append(summary)

    return pd.DataFrame(rows)



def calculate_hierarchical_r2(
        df, 
        metrics=[
        "overallScore", "remScore", "deepScore",
        "lightScore", "recoveryScore", "avgSleepStress"],
        duration_col = "sleep_hours", 
        bedtime_col = "decimalStartTime"):
    
    """Calculates hierarchical ΔR² breakdown (Duration, +Bedtime, +Interaction) globally across metrics."""

    results = []

    for metric in metrics:

        valid = df.dropna(
            subset=[
                metric,
                duration_col,
                bedtime_col
            ]
        ).copy()

        # Centre predictors
        valid["dur_c"] = (
            valid[duration_col]
            - valid[duration_col].mean()
        )

        valid["bed_c"] = (
            valid[bedtime_col]
            - valid[bedtime_col].mean()
        )

        valid["bed_sq"] = valid["bed_c"] ** 2

        valid["dur_bed"] = (
            valid["dur_c"] * valid["bed_c"]
        )

        # Model 1: Sleep duration only
        m1 = smf.ols(
            f"{metric} ~ dur_c",
            data=valid
        ).fit()

        # Model 2: Add bedtime
        m2 = smf.ols(
            f"{metric} ~ dur_c + bed_c",
            data=valid
        ).fit()

        # Model 3: Add nonlinear bedtime
        m3 = smf.ols(
            f"{metric} ~ dur_c + bed_c + bed_sq",
            data=valid
        ).fit()

        # Model 4: Add duration × bedtime interaction
        m4 = smf.ols(
            f"{metric} ~ dur_c + bed_c + bed_sq + dur_bed",
            data=valid
        ).fit()

        # Store hierarchical variance decomposition
        results.append({

            "Metric": metric,
            "N": len(valid),
            "Duration R²":
                m1.rsquared,
            "Bedtime +ΔR²":
                m2.rsquared - m1.rsquared,
            "Quadratic +ΔR²":
                m3.rsquared - m2.rsquared,
            "Interaction +ΔR²":
                m4.rsquared - m3.rsquared,
            "Total R²":
                m4.rsquared,
            "Bedtime p":
                m2.pvalues["bed_c"],
            "Quadratic p":
                m3.pvalues["bed_sq"],
            "Interaction p":
                m4.pvalues["dur_bed"]
        })

    return pd.DataFrame(results)



def calculate_binned_r2_breakdown(
        df,
        metrics=[
        "overallScore", "remScore", "deepScore",
        "lightScore", "recoveryScore", "avgSleepStress"],
        bins=[0, 7, 8, 9, 24],
        labels=["<7h", "7-8h", "8-9h", "9h+"],
        duration_col="sleep_hours",
        bedtime_col="decimalStartTime"):

    """Calculates hierarchical R² variance breakdown across sleep duration bins."""
    
    df["sleep_bin"] = pd.cut(
        df[duration_col], bins=bins, labels=labels, right=False
    )

    plot_data = []

    for b_label in labels:
        subset = df[df["sleep_bin"] == b_label]

        for metric in metrics:
            if len(subset) < 10:
                continue

            # Model 1: Duration alone
            m1 = smf.ols(f"{metric} ~ {duration_col}", data=subset).fit()
            r2_dur = max(0, m1.rsquared * 100)

            # Model 2: Duration + Bedtime (Additive)
            m2 = smf.ols(
                f"{metric} ~ {duration_col} + {bedtime_col}", data=subset
            ).fit()
            r2_add = max(0, m2.rsquared * 100)
            delta_r2_bed = max(0, r2_add - r2_dur)

            # Model 3: Full Interaction
            m3 = smf.ols(
                f"{metric} ~ {duration_col} * {bedtime_col}", data=subset
            ).fit()
            r2_tot = max(0, m3.rsquared * 100)
            delta_r2_int = max(0, r2_tot - r2_add)

            plot_data.append({
                "Sleep Bin": b_label,
                "Metric": metric,
                "Duration Alone": r2_dur,
                "Bedtime Added": delta_r2_bed,
                "Combo Added": delta_r2_int,
                "Total R2": r2_tot,
            })

    return pd.DataFrame(plot_data)



