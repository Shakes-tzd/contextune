import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import sqlite3
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from datetime import datetime, timedelta

    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    return datetime, mo, pd, plt, sqlite3, timedelta


@app.cell
def _(mo):
    mo.md(
        """
    # Contextune Detection Quality Dashboard

    **Version 0.8.6 Improvements:**
    - Context-aware keyword matching (63% → <15% false positives)
    - Haiku correction logging
    - Selective Haiku triggering (60% cost reduction)

    This dashboard visualizes the impact of these improvements on detection quality, cost, and performance.
    """
    )
    return


@app.cell
def _(mo):
    date_range = mo.ui.slider(
        start=1,
        stop=90,
        value=30,
        label="Days to analyze",
        step=1
    )
    date_range
    return (date_range,)


@app.cell
def _(date_range, datetime, pd, sqlite3, timedelta):
    db_path = ".contextune/observability.db"
    conn = sqlite3.connect(db_path)

    cutoff_date = (datetime.now() - timedelta(days=date_range.value)).timestamp()

    detection_df = pd.read_sql_query(
        f"""
        SELECT
            datetime(timestamp, 'unixepoch') as date,
            command,
            confidence,
            method,
            latency_ms,
            prompt_preview
        FROM detection_history
        WHERE timestamp >= {cutoff_date}
        ORDER BY timestamp DESC
        """,
        conn
    )
    return conn, cutoff_date, detection_df


@app.cell
def _(mo):
    mo.md("""## 1. False Positive Rate Analysis""")
    return


@app.cell
def _(detection_df, pd, plt):
    daily_stats = detection_df.copy()
    daily_stats['date'] = pd.to_datetime(daily_stats['date']).dt.date

    daily_help = daily_stats.groupby('date').agg({
        'command': 'count',
        'prompt_preview': lambda x: (x.str.contains('/ctx:help', case=False, na=False)).sum()
    }).rename(columns={'command': 'total_detections', 'prompt_preview': 'help_detections'})

    daily_help['help_percentage'] = (daily_help['help_detections'] / daily_help['total_detections'] * 100).round(2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(daily_help.index, daily_help['help_percentage'], marker='o', linewidth=2, markersize=6)
    ax1.axhline(y=63, color='r', linestyle='--', label='Pre-improvement (63%)', alpha=0.7)
    ax1.axhline(y=15, color='g', linestyle='--', label='Target (<15%)', alpha=0.7)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('/ctx:help Detection Rate (%)')
    ax1.set_title('False Positive Trend: /ctx:help Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)

    command_dist = detection_df['command'].value_counts().head(10)
    ax2.barh(range(len(command_dist)), command_dist.values, color='steelblue')
    ax2.set_yticks(range(len(command_dist)))
    ax2.set_yticklabels(command_dist.index)
    ax2.set_xlabel('Number of Detections')
    ax2.set_title('Top 10 Detected Commands')
    ax2.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    plt.gca()
    return (daily_help,)


@app.cell
def _(mo):
    mo.md("""## 2. Haiku Correction Effectiveness""")
    return


@app.cell
def _(conn, cutoff_date, pd):
    corrections_df = pd.read_sql_query(
        f"""
        SELECT
            datetime(timestamp, 'unixepoch') as date,
            original_command,
            corrected_command,
            original_confidence,
            correction_accepted,
            total_cost_usd,
            latency_ms,
            reasoning
        FROM model_corrections
        WHERE timestamp >= {cutoff_date}
        ORDER BY timestamp DESC
        """,
        conn
    )
    return (corrections_df,)


@app.cell
def _(corrections_df, plt):
    if len(corrections_df) > 0:
        fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 5))

        acceptance_stats = corrections_df.groupby('correction_accepted').agg({
            'total_cost_usd': ['count', 'mean'],
            'latency_ms': 'mean'
        }).round(4)

        colors = ['#ff6b6b', '#51cf66']
        labels = ['Rejected', 'Accepted']
        sizes = [
            len(corrections_df[corrections_df['correction_accepted'] == 0]),
            len(corrections_df[corrections_df['correction_accepted'] == 1])
        ]

        ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax3.set_title('Haiku Correction Acceptance Rate')

        ax4.scatter(
            corrections_df['original_confidence'],
            corrections_df['latency_ms'],
            c=corrections_df['correction_accepted'],
            cmap='RdYlGn',
            alpha=0.6,
            s=100
        )
        ax4.set_xlabel('Original Detection Confidence')
        ax4.set_ylabel('Haiku Analysis Latency (ms)')
        ax4.set_title('Confidence vs Latency (colored by acceptance)')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.gca()
    else:
        plt.figure(figsize=(10, 3))
        plt.text(0.5, 0.5, 'No Haiku correction data available yet.\nRun some prompts to generate data!',
                ha='center', va='center', fontsize=14)
        plt.axis('off')
        plt.gca()
    return


@app.cell
def _(mo):
    mo.md("""## 3. Cost Savings Analysis""")
    return


@app.cell
def _(corrections_df, detection_df, pd, plt):
    daily_cost = corrections_df.copy()
    daily_cost['date'] = pd.to_datetime(daily_cost['date']).dt.date

    cost_summary = daily_cost.groupby('date').agg({
        'total_cost_usd': ['sum', 'count', 'mean']
    }).reset_index()
    cost_summary.columns = ['date', 'total_cost', 'haiku_calls', 'avg_cost']

    daily_detections = detection_df.copy()
    daily_detections['date'] = pd.to_datetime(daily_detections['date']).dt.date
    daily_detection_counts = daily_detections.groupby('date').size().reset_index(name='total_detections')

    cost_summary = cost_summary.merge(daily_detection_counts, on='date', how='left')
    cost_summary['haiku_usage_pct'] = (cost_summary['haiku_calls'] / cost_summary['total_detections'] * 100).round(2)

    fig3, (ax5, ax6) = plt.subplots(1, 2, figsize=(14, 5))

    ax5.bar(range(len(cost_summary)), cost_summary['total_cost'], color='coral', alpha=0.7)
    ax5.set_xticks(range(len(cost_summary)))
    ax5.set_xticklabels([str(d) for d in cost_summary['date']], rotation=45, ha='right')
    ax5.set_xlabel('Date')
    ax5.set_ylabel('Total Cost (USD)')
    ax5.set_title('Daily Haiku Analysis Cost')
    ax5.grid(True, axis='y', alpha=0.3)

    ax6.plot(range(len(cost_summary)), cost_summary['haiku_usage_pct'],
            marker='o', linewidth=2, markersize=6, color='#5470c6')
    ax6.axhline(y=100, color='r', linestyle='--', label='Pre-improvement (100%)', alpha=0.7)
    ax6.axhline(y=40, color='g', linestyle='--', label='Target (40%)', alpha=0.7)
    ax6.set_xticks(range(len(cost_summary)))
    ax6.set_xticklabels([str(d) for d in cost_summary['date']], rotation=45, ha='right')
    ax6.set_xlabel('Date')
    ax6.set_ylabel('Haiku Usage (%)')
    ax6.set_title('Selective Triggering: % of Prompts Analyzed by Haiku')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.gca()
    return (cost_summary,)


@app.cell
def _(mo):
    mo.md("""## 4. Summary Statistics""")
    return


@app.cell
def _(corrections_df, cost_summary, daily_help, detection_df, mo):
    total_detections_summary = len(detection_df)
    avg_help_rate = daily_help['help_percentage'].mean() if len(daily_help) > 0 else 0
    total_haiku_calls = len(corrections_df)
    total_cost_summary = corrections_df['total_cost_usd'].sum() if len(corrections_df) > 0 else 0
    avg_haiku_usage = cost_summary['haiku_usage_pct'].mean() if len(cost_summary) > 0 else 0

    acceptance_rate = (corrections_df['correction_accepted'].sum() / len(corrections_df) * 100) if len(corrections_df) > 0 else 0

    mo.md(f"""
    ### Key Metrics (Last {len(daily_help)} days)

    **Detection Quality:**
    - Total detections: **{total_detections_summary:,}**
    - Average /ctx:help rate: **{avg_help_rate:.2f}%** (target: <15%)
    - Improvement vs baseline: **{max(0, 63 - avg_help_rate):.1f} percentage points** better

    **Haiku Effectiveness:**
    - Total Haiku analyses: **{total_haiku_calls:,}**
    - Correction acceptance rate: **{acceptance_rate:.1f}%**
    - Average Haiku usage: **{avg_haiku_usage:.1f}%** (target: ~40%)

    **Cost Impact:**
    - Total Haiku cost: **${total_cost_summary:.4f}**
    - Average cost per call: **${(total_cost_summary / total_haiku_calls if total_haiku_calls > 0 else 0):.4f}**
    - Estimated monthly savings: **${((100 - avg_haiku_usage) / 100 * 0.90 * 30):.2f}** (vs 100% Haiku usage)
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ---

    ### How to Use This Dashboard

    1. **Adjust the date range** using the slider at the top
    2. **Monitor trends** in the charts to verify improvements
    3. **Track cost savings** from selective Haiku triggering
    4. **Identify issues** if false positive rate increases

    ### Expected Results (v0.8.6)

    - ✅ /ctx:help detection rate should drop from 63% to <15%
    - ✅ Haiku usage should stabilize around 40% (60% reduction)
    - ✅ Correction acceptance rate indicates Haiku value
    - ✅ Cost trends show significant savings over time

    **Database:** `.contextune/observability.db`
    **Version:** 0.8.6
    **Generated with:** Marimo + Claude Code
    """
    )
    return


if __name__ == "__main__":
    app.run()
