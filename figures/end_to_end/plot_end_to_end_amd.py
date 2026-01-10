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
triton_means = np.array([0.7731, 0.748, 0.8934, 0.9048])
triton_mins = np.array([0.2016, 0.2027, 0.6013, 0.6023])
triton_maxs = np.array([0.9598, 0.9638, 1, 1.1318])

# AddressSanitizer data
asan_means = np.array([3.5248, 3.4235, 3.0456, 1.6078])
asan_mins = np.array([2.2561, 2.1466, 1.4804, 1.4294])
asan_maxs = np.array([6.5686, 5.7644, 7.7598, 2.2114])


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

    # Colors: shades of RGB (102, 166, 103) = #66A667
    triton_color = '#4A8A4B'      # Darker shade
    asan_color = '#82C683'        # Lighter shade

    # Draw bars on both axes
    for ax in [ax1, ax2]:
        ax.bar(x - width/2, triton_means, width,
               label='Triton-Sanitizer',
               color=triton_color, edgecolor='black', linewidth=1)

        ax.bar(x + width/2, asan_means, width,
               label='AddressSanitizer',
               color=asan_color, edgecolor='black', linewidth=1)

    # Draw error bars manually to handle the break
    for i in range(len(labels)):
        # Triton-Sanitizer error bars (all fit in main plot)
        ax1.plot([x[i] - width/2, x[i] - width/2], [triton_mins[i], triton_maxs[i]],
                 color='black', linewidth=1.5)
        ax1.plot([x[i] - width/2 - 0.05, x[i] - width/2 + 0.05], [triton_mins[i], triton_mins[i]],
                 color='black', linewidth=1.5)
        ax1.plot([x[i] - width/2 - 0.05, x[i] - width/2 + 0.05], [triton_maxs[i], triton_maxs[i]],
                 color='black', linewidth=1.5)

        # AddressSanitizer error bars
        # Min cap (always in main plot)
        ax1.plot([x[i] + width/2 - 0.05, x[i] + width/2 + 0.05], [asan_mins[i], asan_mins[i]],
                 color='black', linewidth=1.5)

        # Line and max cap depend on whether max is in break range
        if asan_maxs[i] <= 3.99:
            # All in main plot
            ax1.plot([x[i] + width/2, x[i] + width/2], [asan_mins[i], asan_maxs[i]],
                     color='black', linewidth=1.5)
            ax1.plot([x[i] + width/2 - 0.05, x[i] + width/2 + 0.05], [asan_maxs[i], asan_maxs[i]],
                     color='black', linewidth=1.5)
        else:
            # Line goes to top of main plot, continues in top plot
            ax1.plot([x[i] + width/2, x[i] + width/2], [asan_mins[i], 3.99],
                     color='black', linewidth=1.5)
            ax2.plot([x[i] + width/2, x[i] + width/2], [5.5, asan_maxs[i]],
                     color='black', linewidth=1.5)
            ax2.plot([x[i] + width/2 - 0.05, x[i] + width/2 + 0.05], [asan_maxs[i], asan_maxs[i]],
                     color='black', linewidth=1.5)

    # Set axis ranges
    ax1.set_ylim(0, 3.99)
    ax2.set_ylim(5.5, 8)

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

    # Break marks at specific bar positions (indices 0, 1, 2 have max > 4.5)
    # Convert data coordinates to axes coordinates for x positions
    xlim = ax1.get_xlim()
    for idx in range(len(labels)):
        if asan_maxs[idx] > 3.99:
            bar_x = x[idx] + width/2  # AddressSanitizer bar position
            # Convert to axes coordinates
            x_axes = (bar_x - xlim[0]) / (xlim[1] - xlim[0])

            # Draw break marks at this x position
            ax1.plot((x_axes - d, x_axes + d), (1 - d_ax1, 1 + d_ax1), transform=ax1.transAxes, **kwargs)
            ax2.plot((x_axes - d, x_axes + d), (-d_ax2, +d_ax2), transform=ax2.transAxes, **kwargs)

    # Legend (in top subplot)
    ax2.legend(loc='upper right', fontsize=16)
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

        # AddressSanitizer annotations
        # Avg (above bar height)
        ax1.text(x[i] + width/2 - 0.01, asan_means[i] + 0.01,
                f'{asan_means[i]:.2f}x', ha='center', va='bottom', fontsize=24)
        # Min (below min cap)
        ax1.text(x[i] + width/2, asan_mins[i] - 0.02,
                f'{asan_mins[i]:.2f}', ha='center', va='top', fontsize=24)
        # Max (above max cap)
        if asan_maxs[i] <= 3.99:
            ax1.text(x[i] + width/2, asan_maxs[i] + 0.02,
                    f'{asan_maxs[i]:.2f}', ha='center', va='bottom', fontsize=24)
        else:
            ax2.text(x[i] + width/2, asan_maxs[i] + 0.02,
                    f'{asan_maxs[i]:.2f}', ha='center', va='bottom', fontsize=24)

    plt.tight_layout()
    plt.subplots_adjust(left=0.12)
    plt.savefig('end_to_end_amd.pdf', bbox_inches='tight')
    plt.close()
    print("Saved to end_to_end_amd.pdf")


def print_table():
    """Print table"""
    print("| Configuration          | Triton-Sanitizer              | AddressSanitizer             |")
    print("|------------------------|-------------------------------|-------------------------------|")
    for i, label in enumerate(labels):
        label_clean = label.replace('\n', ' ')
        triton_str = f"{triton_means[i]:.4f}x ({triton_mins[i]:.4f}x–{triton_maxs[i]:.4f}x)"
        asan_str = f"{asan_means[i]:.4f}x ({asan_mins[i]:.4f}x–{asan_maxs[i]:.4f}x)"
        print(f"| {label_clean:<22} | {triton_str:<29} | {asan_str:<29} |")


if __name__ == '__main__':
    print_table()
    plot_grouped_bars_broken()
