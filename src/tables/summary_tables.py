

#  Convert decimal bedtime values back into readable clock times for interpretation.
def decimal_to_time(t):
    t = t % 24
    h = int(t)
    m = int(round((t - h) * 60))
    
    if m == 60:
        h = (h + 1) % 24
        m = 0
        
    return f"{h:02d}:{m:02d}"



def binned_bedtime_table(binned_sleep):
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


