import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import io

# --- CONFIGURATION FOR MULTI-CAM ANALYSIS (TASK 5) ---
OUTPUT_CSV_LOCAL_MULTI = "database_multi.csv"
OUTPUT_CSV_VM_MULTI = "az_vm_results_multi.csv"
OUTPUT_CSV_AZURE_MULTI = "az_ai_results_multi.csv"


def analyze_sls_results(file_path, title_prefix):
    """
    Loads a CSV file and calculates key performance metrics (Response Time, Count, and VM Metrics).
    Includes logic for multi-camera analysis if 'camera_id' is present.
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

    # Standardize column name usage
    TIME_COL = 'response_time_s'
    if TIME_COL not in df.columns:
        TIME_COL = 'proc_time_s'

    # --- 1. CORE PERFORMANCE METRICS (Response Time & Detection Output) ---
    print(f"\n\n=======================================================")
    print(f"--- {title_prefix} PERFORMANCE SUMMARY ---")
    print(f"=======================================================")

    # Overall Metrics
    avg_resp_time = df[TIME_COL].mean()
    std_resp_time = df[TIME_COL].std()
    fps = 1 / avg_resp_time if avg_resp_time > 0 else 0
    avg_people_count = df['people_count'].mean()

    print(f"Total Frames Processed: {len(df)}")
    print(f"Average Response Time (ALL): {avg_resp_time:.4f} seconds/frame")
    print(f"Standard Deviation: {std_resp_time:.4f} seconds/frame")
    print(f"Average Frames Per Second (FPS): {fps:.2f} FPS")
    print(
        f"Average People Count (Detection Efficiency): {avg_people_count:.2f} people/frame")

    # --- 2. MULTI-CAMERA ANALYSIS (TASK 5) ---
    if 'camera_id' in df.columns:
        print("\n--- Multi-Camera Analysis: Performance per Camera ---")

        # Calculate mean response time for each camera
        cam_performance = df.groupby('camera_id')[
            TIME_COL].agg(['mean', 'std'])

        # Generate string output of the table for printing
        table_output = io.StringIO()
        cam_performance.sort_values(by='mean', ascending=False).to_markdown(
            table_output, numalign="left", stralign="left")
        print(table_output.getvalue())

        # Plot Response Time by Camera ID
        plt.figure(figsize=(12, 6))

        # Plot time series for each camera
        for cam_id in df['camera_id'].unique():
            cam_df = df[df['camera_id'] == cam_id]
            plt.plot(cam_df['time_elapsed'], cam_df[TIME_COL],
                     marker='.', linestyle='-', markersize=2, label=cam_id)

        plt.title(
            f'{title_prefix} Response Time by Individual Camera (Concurrency Test)')
        plt.xlabel('Time Elapsed (seconds)')
        plt.ylabel('Response Time (seconds/frame)')
        plt.legend(title='Camera ID', loc='upper right')
        plt.grid(True)

        plt.savefig(
            f'{title_prefix.lower().replace(" ", "_")}_multi_cam_timeseries.png')
        plt.close()
        print(
            f"Plot saved: {title_prefix.lower().replace(' ', '_')}_multi_cam_timeseries.png")

    # --- 3. VM/CLOUD SPECIFIC METRICS (Part 2 and Part 4 Data) ---
    vm_cols = ['cpu_util_%', 'mem_used_mb', 'bandwidth_kb', 'cost_unit']
    is_vm_data = all(col in df.columns for col in vm_cols)

    if is_vm_data:
        print("\n--- VM/Cloud Resource Metrics ---")

        for col_name in vm_cols:
            avg_val = df[col_name].mean()
            std_val = df[col_name].std()

            if col_name == 'cpu_util_%':
                print(
                    f"Processor Utilization (CPU): Avg {avg_val:.2f}%, Std {std_val:.2f}%")
            elif col_name == 'mem_used_mb':
                print(f"Memory Used: Avg {avg_val:.2f}MB, Std {std_val:.2f}MB")
            elif col_name == 'bandwidth_kb':
                print(
                    f"Bandwidth Consumed: Avg {avg_val:.2f}KB, Std {std_val:.2f}KB")
            elif col_name == 'cost_unit':
                total_cost = df[col_name].sum()
                print(f"Monetary Cost: Total {total_cost:.8f} units")

        # Plot 3 in 1: CPU, Memory, and Bandwidth over time
        fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        fig.suptitle(
            f'{title_prefix} VM Resource Utilization Over Time', fontsize=16)

        axes[0].plot(df['time_elapsed'], df['cpu_util_%'],
                     color='red', label='CPU Util (%)')
        axes[0].set_ylabel('CPU Utilization (%)')
        axes[0].grid(True, axis='y')

        axes[1].plot(df['time_elapsed'], df['mem_used_mb'],
                     color='blue', label='Memory Used (MB)')
        axes[1].set_ylabel('Memory Used (MB)')
        axes[1].grid(True, axis='y')

        axes[2].plot(df['time_elapsed'], df['bandwidth_kb'],
                     color='green', label='Bandwidth (KB)')
        axes[2].set_ylabel('Bandwidth (KB)')
        axes[2].set_xlabel('Time Elapsed (seconds)')
        axes[2].grid(True, axis='y')

        plt.savefig(f'{title_prefix.lower().replace(" ", "_")}_vm_metrics.png')
        plt.close()
        print(
            f"Plot saved: {title_prefix.lower().replace(' ', '_')}_vm_metrics.png")

    # --- 4. COMMON PLOTS: Overall Response Time and Distribution ---
    # Time Series Plot: Response Time
    plt.figure(figsize=(10, 5))
    plt.plot(df['time_elapsed'], df[TIME_COL],
             marker='.', linestyle='-', markersize=4)
    plt.title(f'{title_prefix} Overall Response Time Over Run Duration')
    plt.xlabel('Time Elapsed (seconds)')
    plt.ylabel('Response Time (seconds/frame)')
    plt.grid(True)
    plt.savefig(f'{title_prefix.lower().replace(" ", "_")}_time_series.png')
    plt.close()

    # Histogram: Distribution of Response Times
    plt.figure(figsize=(8, 5))
    plt.hist(df[TIME_COL], bins=20, edgecolor='black')
    plt.title(f'{title_prefix} Response Time Distribution')
    plt.xlabel('Response Time (seconds/frame)')
    plt.ylabel('Frequency (Frames)')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f'{title_prefix.lower().replace(" ", "_")}_histogram.png')
    plt.close()

    print(
        f"Plots saved: {title_prefix.lower().replace(' ', '_')}_time_series.png and _histogram.png")


if __name__ == "__main__":
    # Analyze Task 5 Multi-Cam Experiments

    # 1. Local Processing Multi-Cam (Baseline)
    analyze_sls_results(OUTPUT_CSV_LOCAL_MULTI, "Part 5 Local Multi-Cam")

    # 2. VM Self-Hosted YOLO Multi-Cam (Part 2 Concurrency)
    analyze_sls_results(OUTPUT_CSV_VM_MULTI, "Part 5 VM YOLO Multi-Cam")

    # 3. Azure AI Service Multi-Cam (Part 4 Concurrency)
    analyze_sls_results(OUTPUT_CSV_AZURE_MULTI, "Part 5 Azure AI Multi-Cam")
