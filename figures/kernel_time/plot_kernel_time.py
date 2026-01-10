import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Data preparation
# ==========================================
platforms = ['NVIDIA', 'AMD']

# Triton-Sanitizer data
triton_means = np.array([10.2151, 10.1125])
triton_mins = np.array([0.038, 0.1095])
triton_maxs = np.array([178.946, 159.8284])

# Vendor sanitizer data (compute-sanitizer for NVIDIA, AddressSanitizer for AMD)
vendor_means = np.array([34.0631, 2.0976])
vendor_mins = np.array([0.3654, 0.9449])
vendor_maxs = np.array([238.665, 2.8926])

vendor_labels = ['compute-sanitizer', 'AddressSanitizer']


def plot_horizontal_bars_broken():
    """Horizontal bar chart with broken x-axis for outlier max values"""

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
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(14, 5),
                                    gridspec_kw={'width_ratios': [4, 1], 'wspace': 0.02})

    y = np.arange(len(platforms))
    height = 0.35  # Height of each bar

    # Colors per platform
    # NVIDIA: Blue shades (from plot_end_to_end.py)
    nvidia_triton_color = '#4A7DB8'      # Darker blue
    nvidia_vendor_color = '#8AADD2'      # Lighter blue
    # AMD: Green shades (from plot_end_to_end_amd.py)
    amd_triton_color = '#4A8A4B'         # Darker green
    amd_vendor_color = '#82C683'         # Lighter green

    triton_colors = [nvidia_triton_color, amd_triton_color]
    vendor_colors = [nvidia_vendor_color, amd_vendor_color]

    # Draw bars on both axes - grouped by platform
    for ax in [ax1, ax2]:
        for i in range(len(platforms)):
            # Triton-Sanitizer bars (bottom of each group)
            ax.barh(y[i] - height/2, triton_means[i], height,
                   label='Triton-Sanitizer' if i == 0 else '',
                   color=triton_colors[i], edgecolor='black', linewidth=1)

            # Vendor sanitizer bars (top of each group)
            ax.barh(y[i] + height/2, vendor_means[i], height,
                   label='Vendor Sanitizer' if i == 0 else '',
                   color=vendor_colors[i], edgecolor='black', linewidth=1)

    # Draw error bars manually to handle the break
    for i in range(len(platforms)):
        # Triton-Sanitizer error bars
        clipped_max_triton = min(triton_maxs[i], 35)
        ax1.plot([triton_mins[i], clipped_max_triton], [y[i] - height/2, y[i] - height/2],
                 color='black', linewidth=1.5)
        # Min cap
        ax1.plot([triton_mins[i], triton_mins[i]], [y[i] - height/2 - 0.08, y[i] - height/2 + 0.08],
                 color='black', linewidth=1.5)
        # Max cap (only if not clipped)
        if triton_maxs[i] <= 35:
            ax1.plot([triton_maxs[i], triton_maxs[i]], [y[i] - height/2 - 0.08, y[i] - height/2 + 0.08],
                     color='black', linewidth=1.5)
        else:
            # Continue in right subplot
            ax2.plot([150, triton_maxs[i]], [y[i] - height/2, y[i] - height/2],
                     color='black', linewidth=1.5)
            ax2.plot([triton_maxs[i], triton_maxs[i]], [y[i] - height/2 - 0.08, y[i] - height/2 + 0.08],
                     color='black', linewidth=1.5)

        # Vendor sanitizer error bars
        clipped_max_vendor = min(vendor_maxs[i], 35)
        ax1.plot([vendor_mins[i], clipped_max_vendor], [y[i] + height/2, y[i] + height/2],
                 color='black', linewidth=1.5)
        # Min cap
        ax1.plot([vendor_mins[i], vendor_mins[i]], [y[i] + height/2 - 0.08, y[i] + height/2 + 0.08],
                 color='black', linewidth=1.5)
        # Max cap (only if not clipped)
        if vendor_maxs[i] <= 35:
            ax1.plot([vendor_maxs[i], vendor_maxs[i]], [y[i] + height/2 - 0.08, y[i] + height/2 + 0.08],
                     color='black', linewidth=1.5)
        else:
            # Continue in right subplot
            ax2.plot([150, vendor_maxs[i]], [y[i] + height/2, y[i] + height/2],
                     color='black', linewidth=1.5)
            ax2.plot([vendor_maxs[i], vendor_maxs[i]], [y[i] + height/2 - 0.08, y[i] + height/2 + 0.08],
                     color='black', linewidth=1.5)

    # Set axis ranges
    ax1.set_xlim(0, 35)
    ax2.set_xlim(150, 250)

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

    # Set y ticks
    ax1.set_yticks(y)
    ax1.set_yticklabels(platforms)

    # Set x ticks
    ax1.set_xticks([1, 10, 20, 30])
    ax2.set_xticks([200])

    # Set y-axis range first (needed for break mark calculations)
    ylim = (-0.6, len(platforms) - 0.4)
    ax1.set_ylim(ylim)

    # Draw break marks
    d = 0.015  # Length of break marks
    d2 = d * 4  # Scale for narrower subplot
    slope = 2  # Slope multiplier to increase angle

    kwargs = dict(color='k', clip_on=False, linewidth=1.5)

    # Break marks at y-axis edges
    ax1.plot((1 - d, 1 + d), (-d*slope, +d*slope), transform=ax1.transAxes, **kwargs)
    ax2.plot((-d2, +d2), (-d*slope, +d*slope), transform=ax2.transAxes, **kwargs)

    # Break marks for bars with max > 35
    for i in range(len(platforms)):
        # Triton-Sanitizer bar
        if triton_maxs[i] > 35:
            bar_y = y[i] - height/2
            y_axes = (bar_y - ylim[0]) / (ylim[1] - ylim[0])
            ax1.plot((1 - d, 1 + d), (y_axes - d*slope, y_axes + d*slope), transform=ax1.transAxes, **kwargs)
            ax2.plot((-d2, +d2), (y_axes - d*slope, y_axes + d*slope), transform=ax2.transAxes, **kwargs)

        # Vendor sanitizer bar
        if vendor_maxs[i] > 35:
            bar_y = y[i] + height/2
            y_axes = (bar_y - ylim[0]) / (ylim[1] - ylim[0])
            ax1.plot((1 - d, 1 + d), (y_axes - d*slope, y_axes + d*slope), transform=ax1.transAxes, **kwargs)
            ax2.plot((-d2, +d2), (y_axes - d*slope, y_axes + d*slope), transform=ax2.transAxes, **kwargs)

    # Legend (swap order: Vendor Sanitizer on top, Triton-Sanitizer on bottom)
    handles, labels = ax1.get_legend_handles_labels()
    ax2.legend(handles[::-1], labels[::-1], loc='upper right', fontsize=20)

    # Add value annotations (avg with min/max in parentheses)
    for i in range(len(platforms)):
        # Triton-Sanitizer annotations (move up and left for bars with high values)
        triton_label = f'{triton_means[i]:.2f}x (min: {triton_mins[i]:.2f}, max: {triton_maxs[i]:.2f})'
        triton_y_offset = 0.08 if triton_means[i] > 5 else 0
        triton_x_offset = 1
        ax1.text(triton_means[i] + triton_x_offset, y[i] - height/2 + triton_y_offset,
                triton_label, va='center', ha='left', fontsize=24)

        # Vendor sanitizer annotations (move up and left for bars with high values)
        vendor_label = f'{vendor_means[i]:.2f}x (min: {vendor_mins[i]:.2f}, max: {vendor_maxs[i]:.2f})'
        vendor_y_offset = 0.25 if vendor_means[i] > 30 else (0.08 if vendor_means[i] > 5 else 0)
        vendor_x_offset = -32 if vendor_means[i] > 5 else 1
        vendor_fontsize = 24
        ax1.text(vendor_means[i] + vendor_x_offset, y[i] + height/2 + vendor_y_offset,
                vendor_label, va='center', ha='left', fontsize=vendor_fontsize)

    # X-axis label (centered across both subplots)
    fig.text(0.5, 0.02, 'Overhead', ha='center', fontsize=30)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    plt.savefig('kernel_time.pdf', bbox_inches='tight')
    plt.close()
    print("Saved to kernel_time.pdf")


def print_table():
    """Print table"""
    print("| Platform | Triton-Sanitizer              | Vendor Sanitizer              |")
    print("|----------|-------------------------------|-------------------------------|")
    for i, platform in enumerate(platforms):
        triton_str = f"{triton_means[i]:.4f}x ({triton_mins[i]:.4f}x–{triton_maxs[i]:.4f}x)"
        vendor_str = f"{vendor_means[i]:.4f}x ({vendor_mins[i]:.4f}x–{vendor_maxs[i]:.4f}x)"
        print(f"| {platform:<8} | {triton_str:<29} | {vendor_str:<29} |")


if __name__ == '__main__':
    print_table()
    plot_horizontal_bars_broken()
