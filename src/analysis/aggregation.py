

def compute_binned_sleep_metrics(
        df, 
        sleep_labels=["<7h", "7-8h", "8-9h", "9h+"], 
        bedtime_labels=[
            "Before 21:00", "21:00-21:30", "21:30-22:00", "22:00-22:30",
            "22:30-23:00", "23:00-23:30", "23:30-00:00", "00:00-00:30",
            "00:30-01:00", "After 01:00"
        ],
        min_nights=5
    ):
    """
    Compute binned sleep metrics across sleep_bin x bedtime_bin.
    Removes sparse cells.
    Returns a clean MultiIndex DataFrame.
    """

    # Aggregate means + counts
    group_stats = (
        df.groupby(["sleep_bin", "bedtime_bin"], observed=True)
          .agg(
              nights=("sleep_hours", "count"),
              overallScore=("overallScore", "mean"),
              remScore=("remScore", "mean"),
              deepScore=("deepScore", "mean"),
              lightScore=("lightScore", "mean"),
              recoveryScore=("recoveryScore", "mean"),
              avgSleepStress=("avgSleepStress", "mean"),
          )
          .round(2)
    )

    # Remove sparse cells
    sparse_mask = group_stats["nights"] < min_nights
    group_stats.loc[sparse_mask, group_stats.columns != "nights"] = float("nan")

    # Reindex MultiIndex levels (NOT pivot)
    group_stats = (
        group_stats
        .reindex(index=sleep_labels, level="sleep_bin")
        .reindex(index=bedtime_labels, level="bedtime_bin")
    )

    return group_stats



def compute_binned_sleep_stats(df, min_nights=20):
    """
    Compute aggregated sleep statistics across bedtime bins.
    Filters out bins with fewer than `min_nights` samples.
    """
    grouped = (
        df.groupby("bedtime_bin", observed=True)
        .agg(
            nights=("sleep_hours", "count"),
            avg_bedtime=("decimalStartTime", "mean"),
            avg_wake_time=("decimalEndTime", "mean"),
            std_wake_time=("decimalEndTime", "std"),
            avg_sleep_hours=("sleep_hours", "mean"),
            std_sleep=("sleep_hours", "std"),
        )
    )

    return grouped.query(f"nights >= {min_nights}")

