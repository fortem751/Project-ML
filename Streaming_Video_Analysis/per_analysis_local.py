import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_CSV_LOCAL = "database.csv"
OUTPUT_CSV_VM = "az_vm_results.csv"


def analyze_sls_results(file_path, title_prefix):
    """
    Loads a CSV file and calculates key performance metrics (Response Time, Count, and VM Metrics).
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Analysis failed. File not found: {file_path}")
        return

    # Ensure timestamp is datetime and calculate elapsed time for plotting
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['time_elapsed'] = (
        df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

    # --- 1. CORE PERFORMANCE METRICS (Response Time & Detection Output) ---
    print(f"\n--- {title_prefix} Performance Summary ---")

    # Response Time (Response Time)
    avg_resp_time = df['response_time_s'].mean()
    std_resp_time = df['response_time_s'].std()
    fps = 1 / avg_resp_time if avg_resp_time > 0 else 0

    print(f"Total Frames Processed: {len(df)}")
    print(f"Average Response Time: {avg_resp_time:.4f} seconds/frame")
    print(
        f"Standard Deviation of Response Time: {std_resp_time:.4f} seconds/frame")
    print(f"Average Frames Per Second (FPS): {fps:.2f} FPS")

    # Detection Output (A surrogate for 'Detection Efficiency')
    avg_people_count = df['people_count'].mean()
    print(
        f"Average People Count: {avg_people_count:.2f} people/frame (Detection Efficiency Metric)")

    # --- 2. VM/CLOUD SPECIFIC METRICS ---
    # Check if VM-specific columns exist (they won't in database.csv)
    vm_cols = ['cpu_util_%', 'mem_used_mb', 'bandwidth_kb', 'cost_unit']
    is_vm_data = all(col in df.columns for col in vm_cols)

    if is_vm_data:
        print("\n--- VM/Cloud Resource Metrics ---")

        # Calculate and print metrics for: Memory Used, Processor Utilization, Bandwidth, Monetary Cost
        for col_name in vm_cols:
            avg_val = df[col_name].mean()
            std_val = df[col_name].std()

            # Format output based on the metric
            if col_name == 'cpu_util_%':
                print(
                    f"Processor Utilization (CPU): Avg {avg_val:.2f}%, Std {std_val:.2f}%")
            elif col_name == 'mem_used_mb':
                print(f"Memory Used: Avg {avg_val:.2f}MB, Std {std_val:.2f}MB")
            elif col_name == 'bandwidth_kb':
                print(
                    f"Bandwidth Consumed: Avg {avg_val:.2f}KB, Std {std_val:.2f}KB")
            elif col_name == 'cost_unit':
                # Assuming cost_unit is in a small monetary unit (e.g., dollars/hour converted to unit/frame)
                total_cost = df[col_name].sum()
                print(f"Monetary Cost: Total {total_cost:.8f} units")

        # --- 3. VM/CLOUD METRICS PLOTTING ---
        # Plot 3 in 1: CPU, Memory, and Bandwidth over time
        fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        fig.suptitle(
            f'{title_prefix} VM Resource Utilization Over Time', fontsize=16)

        # CPU Utilization
        axes[0].plot(df['time_elapsed'], df['cpu_util_%'],
                     color='red', label='CPU Util (%)')
        axes[0].set_ylabel('CPU Utilization (%)')
        axes[0].grid(True, axis='y')

        # Memory Used
        axes[1].plot(df['time_elapsed'], df['mem_used_mb'],
                     color='blue', label='Memory Used (MB)')
        axes[1].set_ylabel('Memory Used (MB)')
        axes[1].grid(True, axis='y')

        # Bandwidth Consumed
        axes[2].plot(df['time_elapsed'], df['bandwidth_kb'],
                     color='green', label='Bandwidth (KB)')
        axes[2].set_ylabel('Bandwidth (KB)')
        axes[2].set_xlabel('Time Elapsed (seconds)')
        axes[2].grid(True, axis='y')

        plt.savefig(f'{title_prefix.lower().replace(" ", "_")}_vm_metrics.png')
        plt.close()
        print(
            f"Plot saved: {title_prefix.lower().replace(' ', '_')}_vm_metrics.png")

    # --- 4. COMMON PLOTS: Response Time and Distribution ---

    # Time Series Plot: Response Time
    plt.figure(figsize=(10, 5))
    plt.plot(df['time_elapsed'], df['response_time_s'],
             marker='.', linestyle='-', markersize=4)
    plt.title(f'{title_prefix} Response Time Over Run Duration')
    plt.xlabel('Time Elapsed (seconds)')
    plt.ylabel('Response Time (seconds/frame)')
    plt.grid(True)
    plt.savefig(f'{title_prefix.lower().replace(" ", "_")}_time_series.png')
    plt.close()

    # Histogram: Distribution of Response Times
    plt.figure(figsize=(8, 5))
    plt.hist(df['response_time_s'], bins=20, edgecolor='black')
    plt.title(f'{title_prefix} Response Time Distribution')
    plt.xlabel('Response Time (seconds/frame)')
    plt.ylabel('Frequency (Frames)')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f'{title_prefix.lower().replace(" ", "_")}_histogram.png')
    plt.close()

    print(
        f"Plots saved: {title_prefix.lower().replace(' ', '_')}_time_series.png and _histogram.png")


if __name__ == "__main__":
    # Analyze Part 1 (Local Work)
    analyze_sls_results(OUTPUT_CSV_LOCAL, "Part 1 Local Work")

    # UNCOMMENT THIS LINE once you have run client.py and server.py to analyze VM data
    analyze_sls_results(OUTPUT_CSV_VM, "Part 2 VM Work")
