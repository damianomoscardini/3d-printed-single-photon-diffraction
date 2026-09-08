"""
High-intensity (non-attenuated) double-slit diffraction pattern: fit the
positions of the diffraction and interference minima against fringe
order to recover the slit width a and separation b.

The film (Kentmere Pan 400, ~40 s exposure, no strong attenuation) is
deliberately overexposed to make the fringes easy to see by eye, which
saturates the film near the pattern's center. Fitting minima *positions*
sidesteps this: a minimum's location doesn't depend on how saturated the
peaks around it are.

The minima positions below were originally measured by eye on this same
scan at 8000 px width, then rescaled to the 3000-px-wide copy shipped in
acquisitions/. To run this on your own image, replace them with pixel
x-coordinates read off *your* scan instead.
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.optimize import curve_fit

# --- Parameters ---
IMAGE_PATH = "acquisitions/double-slit/pattern.jpg"
OUTPUT_PATH = "high_intensity_fit.pdf"

CENTER_X_PX = 1521.375
CENTER_Y_PX = 358
BAND_HEIGHT_PX = 15
PIXEL_SIZE_MM = 140 / 3000  # 140 mm reference width, see README

WAVELENGTH_NM, SIGMA_WAVELENGTH_NM = 520.0, 15.0
DISTANCE_MM, SIGMA_DISTANCE_MM = 4021.0, 5.0

DIFFRACTION_MINIMA_PX = [804.75, 1165.88, 1877.62, 2232.0]
INTERFERENCE_MINIMA_PX = [
    804.75, 848.62, 892.5, 946.5, 1001.62, 1057.12, 1112.62, 1165.88,
    1221.38, 1275.62, 1329.75, 1384.12, 1438.5, 1493.5, 1548.88, 1604.5,
    1657.12, 1712.0, 1766.12, 1821.38, 1877.62, 1930.12, 1985.62, 2041.88,
    2096.38, 2151.75, 2192.62, 2237.62,
]
SIGMA_DIFFRACTION_PX = 22.5
SIGMA_INTERFERENCE_PX = 12.0


def load_intensity_profile(image_path, center_y_px, band_height_px):
    """Average a horizontal band of the image into a 1D intensity
    profile. Intensity is `255 - grayscale` (more film exposure = darker
    pixel = higher intensity)."""
    gray = np.asarray(Image.open(image_path).convert("L"), dtype=float)
    intensity_img = 255.0 - gray
    y1 = max(0, center_y_px - band_height_px // 2)
    y2 = min(gray.shape[0], center_y_px + band_height_px // 2)
    band = intensity_img[y1:y2, :]
    return band.mean(axis=0), band.std(axis=0)


def fringe_orders(n_minima, half_integer_order):
    """Symmetric fringe order for each minimum, skipping order 0: ...,
    -2, -1, 1, 2, ... for diffraction minima, or the same shifted by 1/2
    for interference minima."""
    half = n_minima // 2
    orders = np.concatenate((np.arange(-half, 0), np.arange(1, half + 1)))
    return orders + 0.5 if half_integer_order else orders


def line(n, slope, intercept):
    return slope * n + intercept


def fit_minima(minima_px, center_x_px, sigma_px, half_integer_order):
    """Fit minima positions against fringe order with a straight line.
    Theory: x(n) = (lambda D / length) * n for diffraction minima, or
    x(n) = (lambda D / length) * (n + 1/2) for interference minima --
    the fitted slope is therefore lambda*D/length."""
    positions_px = np.asarray(minima_px, dtype=float) - center_x_px
    orders = fringe_orders(len(positions_px), half_integer_order)

    sigma = np.full_like(positions_px, sigma_px)
    p0 = [positions_px.max() / orders.max(), 0.0]
    popt, pcov = curve_fit(line, orders, positions_px, p0=p0, sigma=sigma, absolute_sigma=True)
    slope_px, intercept_px = popt
    sigma_slope_px = np.sqrt(pcov[0, 0])

    residuals = (positions_px - line(orders, *popt)) / sigma
    chi2_red = np.sum(residuals ** 2) / (len(orders) - 2)
    return slope_px, sigma_slope_px, intercept_px, chi2_red, orders, positions_px


def physical_length(slope_px, sigma_slope_px, pixel_size_mm):
    """length = lambda * D / (slope_px * pixel_size_mm), with the three
    relative uncertainties combined in quadrature."""
    slope_mm = slope_px * pixel_size_mm
    sigma_slope_mm = sigma_slope_px * pixel_size_mm
    length_mm = (WAVELENGTH_NM * 1e-6) * DISTANCE_MM / slope_mm
    rel_err = np.sqrt(
        (SIGMA_WAVELENGTH_NM / WAVELENGTH_NM) ** 2
        + (SIGMA_DISTANCE_MM / DISTANCE_MM) ** 2
        + (sigma_slope_mm / slope_mm) ** 2
    )
    return length_mm, length_mm * rel_err


def main():
    profile, profile_std = load_intensity_profile(IMAGE_PATH, CENTER_Y_PX, BAND_HEIGHT_PX)
    x_mm = (np.arange(len(profile)) - CENTER_X_PX) * PIXEL_SIZE_MM

    diff_slope, diff_sigma_slope, diff_intercept, diff_chi2, diff_orders, diff_pos = fit_minima(
        DIFFRACTION_MINIMA_PX, CENTER_X_PX, SIGMA_DIFFRACTION_PX, half_integer_order=False)
    int_slope, int_sigma_slope, int_intercept, int_chi2, int_orders, int_pos = fit_minima(
        INTERFERENCE_MINIMA_PX, CENTER_X_PX, SIGMA_INTERFERENCE_PX, half_integer_order=True)

    a_mm, sigma_a_mm = physical_length(diff_slope, diff_sigma_slope, PIXEL_SIZE_MM)
    b_mm, sigma_b_mm = physical_length(int_slope, int_sigma_slope, PIXEL_SIZE_MM)

    print(f"Diffraction minima: slope = {diff_slope:.2f} +/- {diff_sigma_slope:.2f} px (reduced chi^2 = {diff_chi2:.3f})")
    print(f"  a = ({a_mm:.3f} +/- {sigma_a_mm:.3f}) mm")
    print(f"Interference minima: slope = {int_slope:.2f} +/- {int_sigma_slope:.2f} px (reduced chi^2 = {int_chi2:.3f})")
    print(f"  b = ({b_mm:.3f} +/- {sigma_b_mm:.3f}) mm")

    # --- Plot: intensity profile on top, minima position vs fringe order below ---
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [1, 2]})

    axs[0].plot(x_mm, profile, "-k")
    axs[0].set_ylabel("Intensity")
    axs[0].grid(True)
    axs[0].tick_params(labelbottom=False)

    for pos, orders, slope, intercept, label, marker, color in [
        (int_pos, int_orders, int_slope, int_intercept, "Interference", "o", "tab:blue"),
        (diff_pos, diff_orders, diff_slope, diff_intercept, "Diffraction", "^", "tab:red"),
    ]:
        axs[1].plot(pos * PIXEL_SIZE_MM, orders, marker, color=color, label=label, markersize=8)
        n_line = np.linspace(orders.min(), orders.max(), 200)
        axs[1].plot(line(n_line, slope, intercept) * PIXEL_SIZE_MM, n_line, "--", color=color, label=f"{label} fit")

    axs[1].set_xlabel("Distance from center [mm]")
    axs[1].set_ylabel("Fringe order $n$")
    axs[1].grid(True)
    axs[1].legend(loc="upper right")

    text = (
        f"a = ({a_mm:.3f} $\\pm$ {sigma_a_mm:.3f}) mm\n"
        f"$\\chi^2_{{red}}$ (diffraction) = {diff_chi2:.2f}\n\n"
        f"b = ({b_mm:.3f} $\\pm$ {sigma_b_mm:.3f}) mm\n"
        f"$\\chi^2_{{red}}$ (interference) = {int_chi2:.2f}"
    )
    axs[1].text(0.02, 0.97, text, ha="left", va="top", transform=axs[1].transAxes,
                bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5", alpha=0.9))

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH)
    plt.show()


if __name__ == "__main__":
    main()
