import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# ==========================================
# Data preparation
# ==========================================
labels = [
    'SymExpr Cache',
    'SymExpr + Loop Cache',
    'SymExpr + Loop +\nGrid Cache',
    'SymExpr + Loop +\nGrid + Kernel Cache'
]

means = np.array([1.0499, 1.1011, 1.9704, 3.1127])
mins = np.array([0.8113, 0.9365, 1.2247, 1.3093])
maxs = np.array([1.2669, 4.4027, 4.6813, 38.9528])


def plot_broken_axis():
    """Horizontal bar chart with broken x-axis for outlier max value"""

    # Error bar values (relative)
    xerr_lower = means - mins
    xerr_upper = maxs - means
    xerr = [xerr_lower, xerr_upper]

    # Style settings (OSDI style)
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif', 'serif'],
        'font.size': 28,
        'axes.labelsize': 30,
        'xtick.labelsize': 28,
        'ytick.labelsize': 24,
    })

    # Create figure with two subplots (left: main data, right: outlier)
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 6),
                                    gridspec_kw={'width_ratios': [4, 1], 'wspace': 0.05})

    # Draw bars on both axes
    for ax in [ax1, ax2]:
        ax.barh(labels, means - 1, left=1, color='gray', edgecolor='black', height=0.5)

    # Draw error bars manually to handle the break
    for i in range(len(labels)):
        # Left part: min to clipped max
        clipped_max = min(maxs[i], 5)
        ax1.plot([mins[i], clipped_max], [i, i], color='black', linewidth=1.5)
        # Min cap
        ax1.plot([mins[i], mins[i]], [i - 0.1, i + 0.1], color='black', linewidth=1.5)
        # Max cap (only if not clipped)
        if maxs[i] <= 5:
            ax1.plot([maxs[i], maxs[i]], [i - 0.1, i + 0.1], color='black', linewidth=1.5)

        # Right part: for the outlier (last bar's max = 38.95)
        if maxs[i] > 5:
            ax2.plot([35, maxs[i]], [i, i], color='black', linewidth=1.5)
            ax2.plot([maxs[i], maxs[i]], [i - 0.1, i + 0.1], color='black', linewidth=1.5)

    # Set axis ranges
    ax1.set_xlim(0.65, 4.75)
    ax2.set_xlim(35, 42)

    # Baseline at x=1
    ax1.axvline(x=1, color='black', linestyle='--', linewidth=1.5, zorder=0)

    # Hide spines between the two axes
    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Remove y-axis ticks on right plot
    ax2.tick_params(axis='y', which='both', length=0)
    ax1.tick_params(axis='y', which='both', length=0)

    # Set x ticks
    ax1.set_xticks([1, 2, 3, 4])
    ax2.set_xticks([40])

    # Draw break marks
    d = 0.015
    # ax2 is 1/4 width of ax1, so scale x by 4 to keep same angle
    d2 = d * 4

    # Calculate y position for last bar in axes coordinates
    # ylim is (-0.6, 3.6), last bar is at y=3
    y_top = (3 - (-0.6)) / (3.6 - (-0.6))  # ≈ 0.857

    kwargs = dict(color='k', clip_on=False, linewidth=1.5)

    # ax1 right edge break marks
    ax1.plot((1 - d, 1 + d), (-d, +d), transform=ax1.transAxes, **kwargs)
    ax1.plot((1 - d, 1 + d), (y_top - d, y_top + d), transform=ax1.transAxes, **kwargs)

    # ax2 left edge break marks (scaled x for same angle)
    ax2.plot((-d2, +d2), (-d, +d), transform=ax2.transAxes, **kwargs)
    ax2.plot((-d2, +d2), (y_top - d, y_top + d), transform=ax2.transAxes, **kwargs)

    # Adjust y-axis range
    ax1.set_ylim(-0.6, len(labels) - 0.4)

    # Add value annotations
    for i in range(len(labels)):
        # Mean annotation
        offset = 0.30 if i == 0 else 0.10
        ax1.text(means[i] + offset, i, f"{means[i]:.2f}x",
                va='center', fontsize=24, fontweight='normal')

        # Min annotation
        ax1.text(mins[i], i - 0.32, f"{mins[i]:.2f}",
                ha='center', va='top', fontsize=22)

        # Max annotation
        if maxs[i] <= 5:
            ax1.text(maxs[i], i - 0.32, f"{maxs[i]:.2f}",
                    ha='center', va='top', fontsize=22)
        else:
            ax2.text(maxs[i], i - 0.32, f"{maxs[i]:.2f}",
                    ha='center', va='top', fontsize=22)

    # X-axis label (centered across both subplots)
    fig.text(0.5, 0.02, 'Speedup', ha='center', fontsize=30)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)

    plt.savefig('ablation_study_new.pdf', bbox_inches='tight')
    plt.close()
    print("Saved to ablation_study_new.pdf")


def print_table():
    """Print table"""
    print("| Optimization Level                    | Overhead Reduction            |")
    print("|---------------------------------------|-------------------------------|")
    for i, label in enumerate(labels):
        reduction_str = f"{means[i]:.3f}x ({mins[i]:.3f}x–{maxs[i]:.3f}x)"
        print(f"| {label:<37} | {reduction_str:<29} |")


if __name__ == '__main__':
    print_table()
    plot_broken_axis()
