import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_bedtime_distribution(df, time_col="decimalStartTime"):
    # 20-minute bins (1/3 hour)
    bin_width = 20 / 60
    bins = np.arange(20, 28.5 + bin_width, bin_width)

    fig, ax = plt.subplots(figsize=(12, 5))

    # Histogram
    ax.hist(
        df[time_col],
        bins=bins,
        edgecolor="white",
        linewidth=0.6,
        alpha=0.7,
        color="#3a7ca5",
        label="Night Count",
    )

    # 80% Core Range
    ax.axvspan(
        df[time_col].quantile(0.10),
        df[time_col].quantile(0.90),
        color="gray",
        alpha=0.12,
        label="80% Core Range",
    )

    # Median Line
    med = df[time_col].median()
    med_time = f"{int(med % 24):02d}:{int((med % 1) * 60):02d}"
    ax.axvline(
        med,
        color="#16425b",
        linestyle="--",
        linewidth=2,
        label=f"Median Bedtime ({med_time})",
    )

    # Axis Formatting
    xticks = np.arange(20, 29)
    xticklabels = [f"{int(x % 24):02d}:00" for x in xticks]

    ax.set_xlabel("Bedtime", labelpad=8)
    ax.set_ylabel("Number of Nights", color="#3a7ca5", fontweight="bold")
    ax.tick_params(axis="y", labelcolor="#3a7ca5")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax.legend(loc="upper right", framealpha=0.9)
    plt.title("Distribution of Bedtimes", fontsize=12, pad=10)
    plt.tight_layout()

    return fig, ax


def plot_sleep_duration_distribution(df, duration_col="sleep_hours", width = 0.25):

    # 15-minute bins default across data range
    min_hrs = np.floor(df[duration_col].min())
    max_hrs = np.ceil(df[duration_col].max())
    bins = np.arange(min_hrs, max_hrs + 0.25, width)

    fig, ax = plt.subplots(figsize=(12, 5))

    # Histogram
    ax.hist(
        df[duration_col],
        bins=bins,
        edgecolor="white",
        linewidth=0.6,
        alpha=0.7,
        color="#3a7ca5",
        label="Night Count",
    )

    # 80% Core Range
    ax.axvspan(
        df[duration_col].quantile(0.10),
        df[duration_col].quantile(0.90),
        color="gray",
        alpha=0.12,
        label="80% Core Range",
    )

    # Median Line
    med = df[duration_col].median()
    ax.axvline(
        med,
        color="#16425b",
        linestyle="--",
        linewidth=2,
        label=f"Median Duration ({med:.2f} hrs)",
    )

    # Axis Formatting
    xticks = np.arange(min_hrs, max_hrs + 1, 1)

    ax.set_xlabel("Sleep Duration (Hours)", labelpad=8)
    ax.set_ylabel("Number of Nights", color="#3a7ca5", fontweight="bold")
    ax.tick_params(axis="y", labelcolor="#3a7ca5")
    ax.set_xticks(xticks)
    ax.set_xticklabels([f"{int(x)}h" for x in xticks])
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax.legend(loc="upper right", framealpha=0.9)
    plt.title("Distribution of Sleep Duration", fontsize=12, pad=10)
    plt.tight_layout()

    return fig, ax


def plot_bedtime_vs_sleep_duration(ax, sleep_df, x_vals, m_dur, c_dur):

    # BEDTIME VS. SLEEP DURATION 
    ax.scatter(
        sleep_df["decimalStartTime"],
        sleep_df["sleep_hours"],
        alpha=0.25,
        s=15,
        color="#1f77b4",
        label="Individual Nights",
    )


    ax.plot(
        x_vals,
        m_dur * x_vals + c_dur,
        color="red",
        linewidth=2,
        linestyle="--",
        label=f"Trendline (slope = {m_dur:.2f} h/hr)",
    )

    ax.set_xticks(range(20, 29))
    ax.set_xticklabels(["20:00", "21:00", "22:00", "23:00", "00:00", "01:00", "02:00", "03:00", "04:00"])

    ax.set_xlabel("Bedtime")
    ax.set_ylabel("Sleep Duration (hours)")
    ax.set_title("Bedtime vs. Sleep Duration (Truncation)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")

    return ax

def plot_bedtime_vs_wake_time(ax, sleep_df, x_vals, m_wake, c_wake):
    #  BEDTIME VS. WAKE TIME (The "Sleeping In" Buffer)

    ax.scatter(
        sleep_df["decimalStartTime"],
        sleep_df["decimalEndTime"],
        alpha=0.25,
        s=15,
        color="#2ca02c",  
        label="Individual Nights",
    )

    ax.plot(
        x_vals,
        m_wake * x_vals + c_wake,
        color="red",
        linewidth=2,
        linestyle="--",
        label=f"Trendline (slope = {m_wake:.2f} h/hr)",
    )

    ax.set_xticks(range(20, 29))
    ax.set_xticklabels(["20:00", "21:00", "22:00", "23:00", "00:00", "01:00", "02:00", "03:00", "04:00"])

    ax.set_yticks(range(5, 12))
    ax.set_yticklabels(
        ["05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00"]
    )
    ax.set_xlabel("Bedtime")
    ax.set_ylabel("Wake Time")
    ax.set_title("Bedtime vs. Wake Time (Partial Compensation)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    return ax


def plot_binned_bedtime(
        binned_sleep, 
        bedtime_labels=[
        "Before 21:00", "21:00-21:30", "21:30-22:00", "22:00-22:30",
        "22:30-23:00", "23:00-23:30", "23:30-00:00", "00:00-00:30",
        "00:30-01:00", "After 01:00"]):

    x_pos = np.arange(len(bedtime_labels))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.5))

    # Sleep Duration
    ax1.plot(
        x_pos,
        binned_sleep["avg_sleep_hours"],
        marker="o",
        linewidth=2.5,
        color="#1f77b4",
        label="Mean Duration",
    )
    # fill the area around the line to show STD 
    ax1.fill_between(
        x_pos,
        binned_sleep["avg_sleep_hours"] - binned_sleep["std_sleep"],
        binned_sleep["avg_sleep_hours"] + binned_sleep["std_sleep"],
        color="#1f77b4",
        alpha=0.18,
        label="±1 Std Dev Range",
    )
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(bedtime_labels, rotation=30, ha="right")
    ax1.set_xlabel("Bedtime Bin")
    ax1.set_ylabel("Sleep Duration (hours)")
    ax1.set_title("Binned Bedtime vs. Sleep Duration")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="lower left")

    # Wake Time Shift
    ax2.plot(
        x_pos,
        binned_sleep["avg_wake_time"],
        marker="s",
        linewidth=2.5,
        color="#2ca02c",
        label="Mean Wake Time",
    )
    ax2.fill_between(
        x_pos,
        binned_sleep["avg_wake_time"] - binned_sleep["std_wake_time"],
        binned_sleep["avg_wake_time"] + binned_sleep["std_wake_time"],
        color="#2ca02c",
        alpha=0.18,
        label="±1 Std Dev Range",
    )
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(bedtime_labels, rotation=30, ha="right")

    ax2.set_xlabel("Bedtime Bin")
    ax2.set_ylabel("Mean Wake Time")
    ax2.set_title("Binned Bedtime vs. Wake Time Shift")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left")

    return fig, ax1, ax2



def plot_metric_heatmaps(
        group_stats, 
        sleep_labels=["<7h", "7-8h", "8-9h", "9h+"],
        bedtime_labels=[
        "Before 21:00", "21:00-21:30", "21:30-22:00", "22:00-22:30",
        "22:30-23:00", "23:00-23:30", "23:30-00:00", "00:00-00:30",
        "00:30-01:00", "After 01:00"], 
        metrics=[
        "overallScore", "remScore", "deepScore",
        "lightScore", "recoveryScore", "avgSleepStress"]):

    plt.figure(figsize=(20, 10))

    for i, metric in enumerate(metrics, 1):

        mean_pivot = (
            group_stats[metric]
            .unstack()
            .reindex(index=sleep_labels[::-1], columns=bedtime_labels)
        )

        plt.subplot(2, 3, i)

        sns.heatmap(
            mean_pivot,
            annot=True,
            fmt=".1f",
            cmap="coolwarm",
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
        )

        plt.title(metric, fontsize=12, weight="bold")
        plt.xlabel("Bedtime" if i > 3 else "")
        plt.ylabel("Sleep Duration" if i in [1, 4] else "")

    plt.tight_layout()



def plot_r2_breakdown(
        viz_df, 
        metrics=[
        "overallScore", "remScore", "deepScore",
        "lightScore", "recoveryScore", "avgSleepStress"]):
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10), sharey=False)
    axes = axes.flatten()

    color_dur = "#1f77b4"
    color_bed = "#ff7f0e"
    color_combo = "#7f7f7f"

    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        m_df = viz_df[viz_df["Metric"] == metric]

        x = np.arange(len(m_df["Sleep Bin"]))
        width = 0.55

        dur = m_df["Duration Alone"].values
        bed = m_df["Bedtime Added"].values
        combo = m_df["Combo Added"].values

        ax.bar(x, dur, width,
               label="Duration Alone ($R^2$)",
               color=color_dur, edgecolor="black", linewidth=0.5)

        ax.bar(x, bed, width,
               bottom=dur,
               label="Bedtime Added ($+\\Delta R^2$)",
               color=color_bed, edgecolor="black", linewidth=0.5)

        ax.bar(x, combo, width,
               bottom=dur + bed,
               label="Combo Added ($+\\Delta R^2$)",
               color=color_combo, edgecolor="black", linewidth=0.5)

        ax.set_title(metric, fontsize=12, fontweight="bold", pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(m_df["Sleep Bin"], fontweight="bold")
        ax.set_ylabel("Variance Explained ($R^2$ %)")
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        for i, tot in enumerate(dur + bed + combo):
            if tot > 0.5:
                ax.text(x[i], tot + 0.8, f"{tot:.1f}%",
                        ha="center", va="bottom",
                        fontsize=8.5, fontweight="bold")

        y_max = max(dur + bed + combo) if len(dur) > 0 else 10
        ax.set_ylim(0, max(y_max * 1.25, 10))

    handles, labels_leg = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels_leg,
               loc="upper center",
               bbox_to_anchor=(0.5, 1.03),
               ncol=3,
               fontsize=11,
               frameon=True,
               facecolor="white",
               edgecolor="none")

    plt.suptitle("Variance Explained (R²) Shift Across Sleep Duration Bins",
                 fontsize=14, fontweight="bold", y=1.06)

    plt.tight_layout()
