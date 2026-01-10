import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Data preparation
# ==========================================
labels = [
    'Compile: On\nMemory: On',
    'Compile: On\nMemory: Off',
    'Compile: Off\nMemory: On',
    'Compile: Off\nMemory: Off'
]

# Triton-Sanitizer data
triton_means = np.array([0.8624, 0.8717, 0.9512, 0.9525])
triton_mins = np.array([0.2084, 0.2384, 0.6663, 0.664])
triton_maxs = np.array([1.0142, 0.9827, 1, 1.0367])

# compute-sanitizer data
compute_means = np.array([1.363, 1.3786, 1.5852, 1.5743])
compute_mins = np.array([1.0849, 1.0814, 1.0921, 1.0838])
compute_maxs = np.array([3.0083, 3.0733, 9.7462, 9.7626])


def plot_grouped_bars_broken():
    """Grouped bar chart with broken y-axis for outlier max values"""

    # Style settings (OSDI style)
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif', 'serif'],
        'font.size': 28,
        'axes.labelsize': 30,
        'xtick.labelsize': 24,
        'ytick.labelsize': 28,
    })

    # Create figure with two subplots (bottom: main data, top: outlier)
    fig, (ax2, ax1) = plt.subplots(2, 1, sharex=True, figsize=(14, 5),
                                    gridspec_kw={'height_ratios': [1, 4], 'hspace': 0.025})

    x = np.arange(len(labels))
    width = 0.35  # Width of each bar

    # Colors: slightly different shades of #6A8DC2
    triton_color = '#4A7DB8'      # Darker shade
    compute_color = '#8AADD2'     # Lighter shade

    # Draw bars on both axes
    for ax in [ax1, ax2]:
        ax.bar(x - width/2, triton_means, width,
               label='Triton-Sanitizer',
               color=triton_color, edgecolor='black', linewidth=1)

        ax.bar(x + width/2, compute_means, width,
               label='compute-sanitizer',
               color=compute_color, edgecolor='black', linewidth=1)

    # Draw error bars manually to handle the break
    for i in range(len(labels)):
        # Triton-Sanitizer error bars (all fit in main plot)
        ax1.plot([x[i] - width/2, x[i] - width/2], [triton_mins[i], triton_maxs[i]],
                 color='black', linewidth=1.5)
        ax1.plot([x[i] - width/2 - 0.05, x[i] - width/2 + 0.05], [triton_mins[i], triton_mins[i]],
                 color='black', linewidth=1.5)
        ax1.plot([x[i] - width/2 - 0.05, x[i] - width/2 + 0.05], [triton_maxs[i], triton_maxs[i]],
                 color='black', linewidth=1.5)

        # compute-sanitizer error bars
        # Min cap (always in main plot)
        ax1.plot([x[i] + width/2 - 0.05, x[i] + width/2 + 0.05], [compute_mins[i], compute_mins[i]],
                 color='black', linewidth=1.5)

        # Line and max cap depend on whether max is in break range
        if compute_maxs[i] <= 3.5:
            # All in main plot
            ax1.plot([x[i] + width/2, x[i] + width/2], [compute_mins[i], compute_maxs[i]],
                     color='black', linewidth=1.5)
            ax1.plot([x[i] + width/2 - 0.05, x[i] + width/2 + 0.05], [compute_maxs[i], compute_maxs[i]],
                     color='black', linewidth=1.5)
        else:
            # Line goes to top of main plot, continues in top plot
            ax1.plot([x[i] + width/2, x[i] + width/2], [compute_mins[i], 3.5],
                     color='black', linewidth=1.5)
            ax2.plot([x[i] + width/2, x[i] + width/2], [9, compute_maxs[i]],
                     color='black', linewidth=1.5)
            ax2.plot([x[i] + width/2 - 0.05, x[i] + width/2 + 0.05], [compute_maxs[i], compute_maxs[i]],
                     color='black', linewidth=1.5)

    # Set axis ranges
    ax1.set_ylim(0, 3.5)
    ax2.set_ylim(9, 10)

    # Add baseline at y=1
    ax1.axhline(y=1, color='black', linestyle='--', linewidth=1.5, zorder=0)

    # Hide spines between the two axes
    ax1.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Tick settings
    ax2.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)

    # Draw break marks
    d = 0.0075
    # ax2 height is 1/5, ax1 height is 4/5, so scale accordingly
    d_ax1 = d  # for ax1 (taller)
    d_ax2 = d * 4  # for ax2 (shorter, need larger value)

    kwargs = dict(color='k', clip_on=False, linewidth=1.5)

    # Y-axis break marks (left edge)
    ax1.plot((-d, +d), (1 - d_ax1, 1 + d_ax1), transform=ax1.transAxes, **kwargs)
    ax2.plot((-d, +d), (-d_ax2, +d_ax2), transform=ax2.transAxes, **kwargs)

    # Break marks at specific bar positions (indices 2 and 3)
    # Convert data coordinates to axes coordinates for x positions
    xlim = ax1.get_xlim()
    for idx in [2, 3]:
        bar_x = x[idx] + width/2  # compute-sanitizer bar position
        # Convert to axes coordinates
        x_axes = (bar_x - xlim[0]) / (xlim[1] - xlim[0])

        # Draw break marks at this x position
        ax1.plot((x_axes - d, x_axes + d), (1 - d_ax1, 1 + d_ax1), transform=ax1.transAxes, **kwargs)
        ax2.plot((x_axes - d, x_axes + d), (-d_ax2, +d_ax2), transform=ax2.transAxes, **kwargs)

    # Legend (in top subplot)
    ax2.legend(loc='upper left', fontsize=16)
    ax1.get_legend().remove() if ax1.get_legend() else None

    # Y-axis label (centered)
    fig.text(0.06, 0.5, 'Overhead', va='center', rotation='vertical', fontsize=30)

    # Add value annotations
    for i in range(len(labels)):
        # Triton-Sanitizer annotations
        # Avg (below bar height)
        ax1.text(x[i] - width/2 - 0.01, triton_means[i] - 0.01,
                f'{triton_means[i]:.2f}x', ha='center', va='top', fontsize=24)
        # Min (below min cap)
        ax1.text(x[i] - width/2, triton_mins[i] - 0.02,
                f'{triton_mins[i]:.2f}', ha='center', va='top', fontsize=24)
        # Max (above max cap)
        ax1.text(x[i] - width/2, triton_maxs[i] + 0.02,
                f'{triton_maxs[i]:.2f}', ha='center', va='bottom', fontsize=24)

        # compute-sanitizer annotations
        # Avg (above bar height)
        ax1.text(x[i] + width/2 - 0.01, compute_means[i] + 0.01,
                f'{compute_means[i]:.2f}x', ha='center', va='bottom', fontsize=24)
        # Min (below min cap)
        ax1.text(x[i] + width/2, compute_mins[i] - 0.02,
                f'{compute_mins[i]:.2f}', ha='center', va='top', fontsize=24)
        # Max (above max cap)
        if compute_maxs[i] <= 3.5:
            ax1.text(x[i] + width/2, compute_maxs[i] + 0.02,
                    f'{compute_maxs[i]:.2f}', ha='center', va='bottom', fontsize=24)
        else:
            ax2.text(x[i] + width/2, compute_maxs[i] + 0.02,
                    f'{compute_maxs[i]:.2f}', ha='center', va='bottom', fontsize=24)

    plt.tight_layout()
    plt.subplots_adjust(left=0.12)
    plt.savefig('end_to_end.pdf', bbox_inches='tight')
    plt.close()
    print("Saved to end_to_end.pdf")


def print_table():
    """Print table"""
    print("| Configuration          | Triton-Sanitizer              | compute-sanitizer             |")
    print("|------------------------|-------------------------------|-------------------------------|")
    for i, label in enumerate(labels):
        label_clean = label.replace('\n', ' ')
        triton_str = f"{triton_means[i]:.4f}x ({triton_mins[i]:.4f}x–{triton_maxs[i]:.4f}x)"
        compute_str = f"{compute_means[i]:.4f}x ({compute_mins[i]:.4f}x–{compute_maxs[i]:.4f}x)"
        print(f"| {label_clean:<22} | {triton_str:<29} | {compute_str:<29} |")


if __name__ == '__main__':
    print_table()
    plot_grouped_bars_broken()
