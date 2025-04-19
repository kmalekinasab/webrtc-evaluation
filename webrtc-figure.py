import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def gather_metrics(json_file, style_map):
    """
    Read the JSON file and extract data for metrics matching keys in style_map.
    Returns a list of dictionaries; each dictionary contains:
      - time_axis: list of datetime objects
      - values: list of floats
      - title: string (e.g. "Round Trip Time (candidate-pair)")
      - y_label: unit for y-axis (e.g., "ms")
      - color: plotting color
      - average: computed average of the values
    """
    with open(json_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
    data = json.loads(content)
    if isinstance(data, list) and len(data) == 1:
        data = data[0]
    
    metrics = []
    for metric_name, metric_info in data.items():
        match_key = None
        for key in style_map:
            if key in metric_name.lower():
                match_key = key
                break
        if not match_key:
            continue

        start_str = metric_info.get("startTime")
        end_str = metric_info.get("endTime")
        raw_values = metric_info.get("values", "[]")
        try:
            start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end_dt   = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        except Exception as e:
            print(f"Error parsing time for {metric_name}: {e}")
            continue

        values_str = raw_values.strip("[]").strip()
        if not values_str:
            continue
        try:
            values = [float(x) for x in values_str.split(",")]
        except ValueError as e:
            print(f"Error parsing numeric values for {metric_name}: {e}")
            continue
        if len(values) < 2:
            continue

        total_duration = end_dt - start_dt
        time_axis = [
            start_dt + total_duration * (i / (len(values) - 1))
            for i in range(len(values))
        ]

        # Build the plot title
        if "roundtriptime" in metric_name.lower():
            base_title = style_map[match_key][0]
            title = base_title
            stats_type = metric_info.get("statsType", "")
            if stats_type:
                title = f"{title} ({stats_type})"
        else:
            title = style_map[match_key][0]

        avg = sum(values) / len(values)
        metrics.append({
            "time_axis": time_axis,
            "values": values,
            "title": title,
            "y_label": style_map[match_key][2],
            "color": style_map[match_key][1],
            "average": avg
        })
    return metrics

def plot_all_metrics(metrics):
    """
    Plot all metrics as subplots in one window.
    Each subplot shares the x-axis with the bottom one, which shows the time labels.
    """
    n = len(metrics)
    if n == 0:
        print("No matching metrics found.")
        return
    
    fig, axs = plt.subplots(nrows=n, ncols=1, figsize=(12, n * 3.5), sharex=True)
    if n == 1:
        axs = [axs]
    
    for i, (ax, met) in enumerate(zip(axs, metrics)):
        ax.plot(met["time_axis"], met["values"],
                color=met["color"], linewidth=2, label="Data")
        ax.fill_between(met["time_axis"], met["values"],
                        color=met["color"], alpha=0.2)
        ax.axhline(met["average"], color="gray", linestyle="--", linewidth=1,
                   label=f"Avg: {met['average']:.2f}")

        # Force y-axis from 0 to (max + 20%)
        y_max = max(met["values"])
        ax.set_ylim(0, y_max * 1.2)

        # Title, labels, ticks
        ax.set_title(met["title"], fontsize=12)
        ax.set_ylabel(met["y_label"], fontsize=10)      # smaller Y-axis label
        ax.tick_params(axis='y', labelsize=9)          # smaller Y-axis tick labels
        ax.grid(True, linestyle="--", alpha=0.5)

        # Legend with reduced font size
        ax.legend(loc="upper right", fontsize=8)

        # Only bottom subplot shows the X-axis
        if i < n - 1:
            ax.label_outer()
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis='x', labelsize=9)
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(0)
            ax.set_xlabel("Time", fontsize=12)
    
    fig.subplots_adjust(top=0.92, bottom=0.08, left=0.1, right=0.95, hspace=0.3)
    plt.show()

def plot_summary_table(metrics):
    """
    Create a separate window with a table summarizing the metric averages.
    """
    summary_data = [
        [met["title"], f"{met['average']:.2f} {met['y_label']}"]
        for met in metrics
    ]
    fig, ax = plt.subplots(figsize=(8, len(summary_data) * 0.5 + 1))
    ax.axis("tight")
    ax.axis("off")
    ax.table(cellText=summary_data,
             colLabels=["Metric", "Average"],
             cellLoc='center', loc='center')
    plt.title("Summary Statistics", fontsize=14)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    style_map = {
        "roundtriptime": ("Round Trip Time", "#f39c12", "ms"),
        "jitter":        ("Jitter", "#c0392b", "ms"),
        "bitrate":       ("Bitrate (Ms)", "#8e44ad", "Kbit/s"),
        "framespersecond": ("Frames Per Second", "#2980b9", "fps"),
        "framewidth":    ("Frame Width", "#27ae60", "pixels"),
        "frameheight":   ("Frame Height", "#2c3e50", "pixels"),
        "framesdecoded/s": ("Frames Decoded per Second", "#27ae60", "frames/s")
    }
    
    # Update this path to point at your JSON file
    json_file = r"C:\Users\malek\OneDrive\Documents\first-term-2025\peer-to peer\project\demo\webrtc-internal_fixed.json"
    
    metrics = gather_metrics(json_file, style_map)
    plot_all_metrics(metrics)
    plot_summary_table(metrics)
