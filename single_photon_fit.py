"""
Single-photon (attenuated) double-slit diffraction pattern: fit the whole
intensity profile directly against the theoretical Fraunhofer intensity
to recover the slit width a and separation b.

The film (Ilford Delta 3200, push-processed to ISO 6400, ~8 h exposure
with all five filters engaged) is exposed slowly enough to stay within
its linear response range, so -- unlike the high-intensity exposure --
the whole profile can be trusted, not just minima positions.
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.optimize import curve_fit

# --- Parameters ---
IMAGE_PATH = "acquisitions/double-slit-single-photon/pattern.jpg"
OUTPUT_PATH = "single_photon_fit.pdf"

CENTER_X_PX = 1493.5
CENTER_Y_PX = 376
BAND_HEIGHT_PX = 40
PIXEL_SIZE_MM = 0.023350  # see README for how this was calibrated

WAVELENGTH_NM, SIGMA_WAVELENGTH_NM = 520.0, 15.0
DISTANCE_MM, SIGMA_DISTANCE_MM = 4091.0, 5.0

INTENSITY_THRESHOLD = 0.1  # exclude points below this fraction of the peak (film grain noise)
A0_MM, B0_MM = 0.1, 0.8    # starting guess for the fit


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


def double_slit_intensity(x, alpha, beta, C):
    """I(x) = C * cos^2(pi x / beta) * sinc^2(x / alpha), with
    alpha = lambda*D/a and beta = lambda*D/b."""
    return C * np.cos(np.pi * x / beta) ** 2 * np.sinc(x / alpha) ** 2


def physical_length(param_mm, sigma_param_mm):
    """length = lambda * D / param, with the three relative
    uncertainties combined in quadrature."""
    length_mm = (WAVELENGTH_NM * 1e-6) * DISTANCE_MM / param_mm
    rel_err = np.sqrt(
        (SIGMA_WAVELENGTH_NM / WAVELENGTH_NM) ** 2
        + (SIGMA_DISTANCE_MM / DISTANCE_MM) ** 2
        + (sigma_param_mm / param_mm) ** 2
    )
    return length_mm, length_mm * rel_err


def main():
    profile, profile_std = load_intensity_profile(IMAGE_PATH, CENTER_Y_PX, BAND_HEIGHT_PX)
    x_mm = (np.arange(len(profile)) - CENTER_X_PX) * PIXEL_SIZE_MM
    peak = np.interp(CENTER_X_PX, np.arange(len(profile)), profile)
    intensity = profile / peak
    intensity_err = profile_std / peak

    mask = intensity >= INTENSITY_THRESHOLD
    x_fit, y_fit, sigma_fit = x_mm[mask], intensity[mask], intensity_err[mask]
    sigma_fit = np.where(sigma_fit > 0, sigma_fit, np.median(sigma_fit[sigma_fit > 0]))

    alpha0 = WAVELENGTH_NM * 1e-6 * DISTANCE_MM / A0_MM
    beta0 = WAVELENGTH_NM * 1e-6 * DISTANCE_MM / B0_MM
    popt, pcov = curve_fit(double_slit_intensity, x_fit, y_fit, p0=[alpha0, beta0, 1.0],
                            sigma=sigma_fit, absolute_sigma=True)
    alpha_mm, beta_mm, C = popt
    sigma_alpha_mm, sigma_beta_mm, sigma_C = np.sqrt(np.diag(pcov))

    residuals = (y_fit - double_slit_intensity(x_fit, *popt)) / sigma_fit
    chi2_red = np.sum(residuals ** 2) / (len(x_fit) - 3)

    a_mm, sigma_a_mm = physical_length(alpha_mm, sigma_alpha_mm)
    b_mm, sigma_b_mm = physical_length(beta_mm, sigma_beta_mm)

    print(f"alpha = ({alpha_mm:.3f} +/- {sigma_alpha_mm:.3f}) mm, beta = ({beta_mm:.3f} +/- {sigma_beta_mm:.3f}) mm, "
          f"C = {C:.3f} +/- {sigma_C:.3f}")
    print(f"reduced chi^2 = {chi2_red:.3f}")
    print(f"a = ({a_mm:.3f} +/- {sigma_a_mm:.3f}) mm")
    print(f"b = ({b_mm:.3f} +/- {sigma_b_mm:.3f}) mm")

    # --- Plot: data + fit overlay ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_mm, intensity, "-k", label="Data")
    ax.fill_between(x_mm, intensity - intensity_err, intensity + intensity_err, color="orange", alpha=0.3, label="Error")
    x_line = np.linspace(x_fit.min(), x_fit.max(), 1000)
    ax.plot(x_line, double_slit_intensity(x_line, *popt), "r--", label="Fit")
    ax.set_xlabel("Distance from center [mm]")
    ax.set_ylabel("Relative intensity")
    ax.grid(True)
    ax.legend(loc="upper right")

    text = (
        f"a = ({a_mm:.3f} $\\pm$ {sigma_a_mm:.3f}) mm\n"
        f"b = ({b_mm:.3f} $\\pm$ {sigma_b_mm:.3f}) mm\n"
        f"C = {C:.3f} $\\pm$ {sigma_C:.3f}\n"
        f"$\\chi^2_{{red}}$ = {chi2_red:.2f}"
    )
    ax.text(0.03, 0.95, text, ha="left", va="top", transform=ax.transAxes,
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5", alpha=0.85))

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH)
    plt.show()


if __name__ == "__main__":
    main()
