"""
Defect Analysis Script for Manufacturing Line
Analyzes defect rates and generates statistical control chart PDF report
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import os

# ---------------- CONFIGURATION ----------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

DATA_FILE = os.path.join(PROJECT_DIR, "data", "defects.xlsx")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, f"statistical_results_{timestamp}.pdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"[Config] Data file  : {DATA_FILE}")
print(f"[Config] Output PDF: {OUTPUT_PDF}")

# ---------------- FUNCTIONS ----------------

def load_data():
    """Load defect data from Excel"""
    return pd.read_excel(DATA_FILE)


def calculate_metrics(df):
    """Calculate defect rate and control chart metrics"""
    df["Defect_Rate"] = df["Defect_Count"] / df["Units_Produced"]

    mean_rate = df["Defect_Rate"].mean()
    std_rate = df["Defect_Rate"].std()
    n = len(df)

    t_crit = stats.t.ppf(0.975, n - 1)
    ci_margin = t_crit * (std_rate / np.sqrt(n))
    ci_lower = mean_rate - ci_margin
    ci_upper = mean_rate + ci_margin

    mean_defects = df["Defect_Count"].mean()
    std_defects = df["Defect_Count"].std()
    ucl = mean_defects + 3 * std_defects
    lcl = max(0, mean_defects - 3 * std_defects)

    return {
        "mean_rate": mean_rate,
        "std_rate": std_rate,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n": n,
        "mean_defects": mean_defects,
        "std_defects": std_defects,
        "ucl": ucl,
        "lcl": lcl
    }


def perform_ttest(df):
    """Perform t-test between Day and Night shifts"""
    day = df[df["Shift"].str.upper() == "DAY"]["Defect_Rate"]
    night = df[df["Shift"].str.upper() == "NIGHT"]["Defect_Rate"]

    t_stat, p_value = stats.ttest_ind(day, night)

    return {
        "day_mean": day.mean(),
        "day_std": day.std(),
        "day_n": len(day),
        "night_mean": night.mean(),
        "night_std": night.std(),
        "night_n": len(night),
        "t_stat": t_stat,
        "p_value": p_value
    }


def plot_control_chart(df, metrics):
    """Create control chart"""
    plt.close("all")

    df["Date_Shift"] = df["Date"].astype(str) + " (" + df["Shift"] + ")"
    x = np.arange(len(df))

    fig, ax = plt.subplots(figsize=(13, 6))

    ax.plot(x, df["Defect_Count"], marker="o", label="Defect Count")
    ax.axhline(metrics["mean_defects"], color="green", linestyle="--", label="CL")
    ax.axhline(metrics["ucl"], color="red", linestyle="--", label="UCL")
    ax.axhline(metrics["lcl"], color="red", linestyle="--", label="LCL")

    ax.set_xlabel("Date (Shift)")
    ax.set_ylabel("Defect Count")
    ax.set_title("Control Chart: Defect Count Over Time")
    ax.set_xticks(x)
    ax.set_xticklabels(df["Date_Shift"], rotation=45, ha="right", fontsize=8)
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    return fig


def create_summary_page(metrics, ttest):
    """Create summary text page"""
    summary = f"""
DEFECT ANALYSIS - STATISTICAL SUMMARY
============================================================

OVERALL DEFECT RATE:
Observations          : {metrics['n']}
Mean Defect Rate      : {metrics['mean_rate']:.6f} ({metrics['mean_rate']*100:.4f}%)
Std Deviation         : {metrics['std_rate']:.6f}
95% Confidence Interval: [{metrics['ci_lower']:.6f}, {metrics['ci_upper']:.6f}]

CONTROL CHART LIMITS:
CL  : {metrics['mean_defects']:.2f}
UCL : {metrics['ucl']:.2f}
LCL : {metrics['lcl']:.2f}

T-TEST (DAY vs NIGHT):
Day Mean    : {ttest['day_mean']:.6f}
Night Mean  : {ttest['night_mean']:.6f}
T-statistic : {ttest['t_stat']:.4f}
P-value     : {ttest['p_value']:.6f}

INTERPRETATION:
"""

    if ttest["p_value"] < 0.05:
        diff = abs(ttest["night_mean"] - ttest["day_mean"]) * 100
        summary += f"Statistically significant difference detected.\nNight shift defect rate is higher by {diff:.4f}%."
    else:
        summary += "No statistically significant difference detected."

    summary += f"""

============================================================
Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================
"""

    fig = plt.figure(figsize=(11, 8.5))
    plt.axis("off")
    plt.text(0.01, 0.99, summary, va="top", ha="left", family="monospace")
    return fig


# ---------------- MAIN ----------------

def main():
    print("\nLoading data...")
    df = load_data()

    print("Calculating metrics...")
    metrics = calculate_metrics(df)

    print("Performing t-test...")
    ttest = perform_ttest(df)

    # ✅ PRINT FOR TERMINAL SCREENSHOT
    print("\nShift-wise Summary:")
    print(df.groupby("Shift")["Defect_Rate"].agg(["mean", "std", "count"]))

    print(f"\n95% Confidence Interval: {metrics['ci_lower']:.4f} to {metrics['ci_upper']:.4f}")
    print(f"T-statistic: {ttest['t_stat']:.4f}")
    print(f"P-value: {ttest['p_value']:.6f}")

    print("\nCreating control chart...")
    chart_fig = plot_control_chart(df, metrics)

    print("Creating summary page...")
    summary_fig = create_summary_page(metrics, ttest)

    print("\nSaving PDF...")
    with PdfPages(OUTPUT_PDF) as pdf:
        pdf.savefig(chart_fig)
        pdf.savefig(summary_fig)

    plt.close("all")
    print(f"\n✓ Analysis complete. Report saved to:\n{OUTPUT_PDF}\n")


if __name__ == "__main__":
    main()
