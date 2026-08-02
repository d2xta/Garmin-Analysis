

def binned_bedtime_table(binned_sleep, decimal_to_time):
    # Clean summary table
    binned_display = binned_sleep[["nights", "avg_wake_time", "avg_sleep_hours", "std_sleep"]].rename(
        columns={
            "nights": "Nights (N)",
            "avg_wake_time": "Mean Wake Time",
            "avg_sleep_hours": "Mean Sleep (hrs)",
            "std_sleep": "Std Dev (hrs)"
        }
    )

    return binned_display.style.format({
        "Mean Sleep (hrs)": "{:.2f}",
        "Std Dev (hrs)": "{:.2f}",
        "Mean Wake Time": lambda x: decimal_to_time(x)
    })


