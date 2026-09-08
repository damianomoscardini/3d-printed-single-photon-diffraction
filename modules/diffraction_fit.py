"""
Cleaned-up, English versions of the two diffraction-pattern analyses
originally used for this project -- one per exposure regime:

- fit_minima_positions(): for the high-intensity (non-attenuated) double-
  slit pattern, deliberately overexposed to make the fringes easy to see
  by eye. The film saturates near the center, so instead of fitting the
  intensity profile, this fits the *positions* of hand-identified minima
  against their fringe order -- a minimum's position doesn't depend on
  how saturated the peaks around it are.

- fit_intensity_profile(): for the single-photon (attenuated) double-slit
  pattern, exposed slowly enough to stay in the film's linear response
  range. Here the whole intensity profile is fit directly against the
  theoretical Fraunhofer intensity.

Both start from the same kind of input: a 1D intensity profile extracted
from a horizontal band of the scanned image (extract_intensity_profile).
Neither method guesses anything about the image on its own -- the center,
band height, and (for method 1) the minima positions are all things you
read off the image yourself, same as in the original analysis.
"""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.optimize import curve_fit


# --------------------------------------------------------------------------
# Profile extraction (shared by both methods)
# --------------------------------------------------------------------------

def load_grayscale(image_path: str) -> np.ndarray:
    """Load an image as a float grayscale array."""
    return np.asarray(Image.open(image_path).convert("L"), dtype=float)


def extract_intensity_profile(
    gray: np.ndarray, center_y_px: int, band_height_px: int = 40,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Average a horizontal band of the image, centered on `center_y_px`
    with height `band_height_px`, into a 1D intensity profile.

    Intensity is `255 - grayscale` (film exposure darkens the film, so
    more exposure = darker pixel = higher intensity). `center_y_px` is
    something you read off the image; it isn't guessed automatically.
    """
    h, w = gray.shape
    intensity_img = 255.0 - gray
    y1 = max(0, center_y_px - band_height_px // 2)
    y2 = min(h, center_y_px + band_height_px // 2)
    band = intensity_img[y1:y2, :]
    return band.mean(axis=0), band.std(axis=0)


# --------------------------------------------------------------------------
# Physical slit size / spacing, with propagated uncertainty
# --------------------------------------------------------------------------

def physical_length(
    param_mm: float, sigma_param_mm: float,
    wavelength_nm: float, sigma_wavelength_nm: float,
    distance_mm: float, sigma_distance_mm: float,
) -> tuple[float, float]:
    """length = lambda * D / param, with the three relative uncertainties
    combined in quadrature (covariances neglected, as in the original
    analysis)."""
    length_mm = (wavelength_nm * 1e-6) * distance_mm / param_mm
    rel_err = np.sqrt(
        (sigma_wavelength_nm / wavelength_nm) ** 2
        + (sigma_distance_mm / distance_mm) ** 2
        + (sigma_param_mm / param_mm) ** 2
    )
    return length_mm, length_mm * rel_err


# --------------------------------------------------------------------------
# Method 1 (high-intensity pattern): fit hand-identified minima positions
# --------------------------------------------------------------------------

@dataclass
class MinimaFitResult:
    slope_px: float
    sigma_slope_px: float
    intercept_px: float
    chi2_red: float
    ndof: int
    orders: np.ndarray
    positions_px: np.ndarray
    length_mm: float
    sigma_length_mm: float


def _line(n, slope, intercept):
    return slope * n + intercept


def _fringe_orders(n_minima: int, half_integer_order: bool) -> np.ndarray:
    """Symmetric fringe order for each minimum, skipping order 0 (there
    is no zeroth minimum): ..., -2, -1, 1, 2, ... for diffraction minima,
    or the same shifted by 1/2 for interference minima."""
    half = n_minima // 2
    orders = np.concatenate((np.arange(-half, 0), np.arange(1, half + 1)))
    return orders + 0.5 if half_integer_order else orders


def fit_minima_positions(
    minima_px, center_x_px: float, sigma_px: float, half_integer_order: bool,
    pixel_size_mm: float,
    wavelength_nm: float, sigma_wavelength_nm: float,
    distance_mm: float, sigma_distance_mm: float,
) -> MinimaFitResult:
    """
    Fit minima positions (raw pixel x-coordinates, as read off the image)
    against their fringe order with a straight line, and convert the
    slope into a physical length.

    Call this once with diffraction (envelope) minima and
    `half_integer_order=False` to get the slit width `a`, and once with
    interference minima and `half_integer_order=True` to get the slit
    separation `b` -- per theory, x(n) = (lambda D / length) * n for
    diffraction minima and x(n) = (lambda D / length) * (n + 1/2) for
    interference minima.
    """
    positions_px = np.asarray(minima_px, dtype=float) - center_x_px
    orders = _fringe_orders(len(positions_px), half_integer_order)

    sigma = np.full_like(positions_px, float(sigma_px))
    p0 = [positions_px.max() / orders.max(), 0.0]
    popt, pcov = curve_fit(_line, orders, positions_px, p0=p0, sigma=sigma, absolute_sigma=True)
    slope_px, intercept_px = popt
    sigma_slope_px = float(np.sqrt(pcov[0, 0]))

    residuals = (positions_px - _line(orders, *popt)) / sigma
    chi2 = float(np.sum(residuals ** 2))
    ndof = len(orders) - 2

    length_mm, sigma_length_mm = physical_length(
        slope_px * pixel_size_mm, sigma_slope_px * pixel_size_mm,
        wavelength_nm, sigma_wavelength_nm, distance_mm, sigma_distance_mm,
    )
    return MinimaFitResult(
        slope_px, sigma_slope_px, float(intercept_px), chi2 / ndof, ndof,
        orders, positions_px, length_mm, sigma_length_mm,
    )


def plot_minima_fit(
    profile_x_mm, intensity,
    diffraction_fit: MinimaFitResult, interference_fit: MinimaFitResult,
    pixel_size_mm: float, title: str | None = None,
):
    """Two-panel plot: intensity profile on top, minima position vs
    fringe order (with both fitted lines) below -- mirrors the original
    script's plot."""
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [1, 2]})

    axs[0].plot(profile_x_mm, intensity, "-k")
    axs[0].set_ylabel("Intensity")
    axs[0].grid(True)
    axs[0].tick_params(labelbottom=False)
    if title:
        axs[0].set_title(title)

    for fit, label, marker, color in [
        (interference_fit, "Interference", "o", "tab:blue"),
        (diffraction_fit, "Diffraction", "^", "tab:red"),
    ]:
        x_mm = fit.positions_px * pixel_size_mm
        axs[1].plot(x_mm, fit.orders, marker, color=color, label=label, markersize=8)
        n_line = np.linspace(fit.orders.min(), fit.orders.max(), 200)
        axs[1].plot(_line(n_line, fit.slope_px, fit.intercept_px) * pixel_size_mm, n_line,
                    "--", color=color, label=f"{label} fit")

    axs[1].set_xlabel("Distance from center [mm]")
    axs[1].set_ylabel("Fringe order $n$")
    axs[1].grid(True)
    axs[1].legend(loc="upper right")

    text = (
        rf"$a$ = ({diffraction_fit.length_mm:.3f} $\pm$ {diffraction_fit.sigma_length_mm:.3f}) mm" "\n"
        rf"$\chi^2_{{red}}$ (diffraction) = {diffraction_fit.chi2_red:.2f}" "\n\n"
        rf"$b$ = ({interference_fit.length_mm:.3f} $\pm$ {interference_fit.sigma_length_mm:.3f}) mm" "\n"
        rf"$\chi^2_{{red}}$ (interference) = {interference_fit.chi2_red:.2f}"
    )
    axs[1].text(0.02, 0.97, text, ha="left", va="top", transform=axs[1].transAxes,
                bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5", alpha=0.9))
    fig.tight_layout()
    return fig, axs


def summarize_minima_fit(diffraction_fit: MinimaFitResult, interference_fit: MinimaFitResult) -> str:
    return (
        f"Diffraction minima: slope = {diffraction_fit.slope_px:.2f} +/- {diffraction_fit.sigma_slope_px:.2f} px "
        f"(reduced chi^2 = {diffraction_fit.chi2_red:.3f}, ndof = {diffraction_fit.ndof})\n"
        f"  a = ({diffraction_fit.length_mm:.3f} +/- {diffraction_fit.sigma_length_mm:.3f}) mm\n"
        f"Interference minima: slope = {interference_fit.slope_px:.2f} +/- {interference_fit.sigma_slope_px:.2f} px "
        f"(reduced chi^2 = {interference_fit.chi2_red:.3f}, ndof = {interference_fit.ndof})\n"
        f"  b = ({interference_fit.length_mm:.3f} +/- {interference_fit.sigma_length_mm:.3f}) mm"
    )


# --------------------------------------------------------------------------
# Method 2 (single-photon pattern): direct fit of the intensity profile
# --------------------------------------------------------------------------

def double_slit_intensity(x, alpha, beta, C):
    """I(x) = C * cos^2(pi x / beta) * sinc^2(x / alpha)."""
    return C * np.cos(np.pi * x / beta) ** 2 * np.sinc(x / alpha) ** 2


@dataclass
class IntensityFitResult:
    alpha_mm: float
    sigma_alpha_mm: float
    beta_mm: float
    sigma_beta_mm: float
    C: float
    sigma_C: float
    chi2_red: float
    ndof: int
    mask: np.ndarray
    a_mm: float
    sigma_a_mm: float
    b_mm: float
    sigma_b_mm: float


def fit_intensity_profile(
    x_mm, intensity, intensity_err, p0,
    wavelength_nm: float, sigma_wavelength_nm: float,
    distance_mm: float, sigma_distance_mm: float,
    intensity_threshold: float = 0.1,
) -> IntensityFitResult:
    """
    Fit the whole normalized intensity profile (peak ~= 1) directly
    against the double-slit Fraunhofer intensity. Points below
    `intensity_threshold` (fraction of the peak) are excluded, since film
    grain noise dominates there -- same cutoff as the original analysis.

    `p0 = [alpha0_mm, beta0_mm, C0]`: a starting guess for the fit, e.g.
    from the slit width/spacing you roughly expect
    (alpha0 = lambda * D / a0, beta0 = lambda * D / b0).
    """
    mask = intensity >= intensity_threshold
    x_fit, y_fit, sigma_fit = x_mm[mask], intensity[mask], intensity_err[mask]
    sigma_fit = np.where(sigma_fit > 0, sigma_fit, np.median(sigma_fit[sigma_fit > 0]))

    popt, pcov = curve_fit(double_slit_intensity, x_fit, y_fit, p0=p0, sigma=sigma_fit, absolute_sigma=True)
    perr = np.sqrt(np.diag(pcov))
    alpha_mm, beta_mm, C = popt
    sigma_alpha_mm, sigma_beta_mm, sigma_C = perr

    residuals = (y_fit - double_slit_intensity(x_fit, *popt)) / sigma_fit
    chi2 = float(np.sum(residuals ** 2))
    ndof = len(x_fit) - 3

    a_mm, sigma_a_mm = physical_length(alpha_mm, sigma_alpha_mm, wavelength_nm, sigma_wavelength_nm, distance_mm, sigma_distance_mm)
    b_mm, sigma_b_mm = physical_length(beta_mm, sigma_beta_mm, wavelength_nm, sigma_wavelength_nm, distance_mm, sigma_distance_mm)

    return IntensityFitResult(
        float(alpha_mm), float(sigma_alpha_mm), float(beta_mm), float(sigma_beta_mm),
        float(C), float(sigma_C), chi2 / ndof, ndof, mask,
        a_mm, sigma_a_mm, b_mm, sigma_b_mm,
    )


def plot_intensity_fit(x_mm, intensity, intensity_err, fit: IntensityFitResult, title: str | None = None):
    """Data + fit overlay + a parameter text box -- mirrors the original
    script's plot."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_mm, intensity, "-k", label="Data")
    ax.fill_between(x_mm, intensity - intensity_err, intensity + intensity_err, color="orange", alpha=0.3, label="Error")

    x_fit = np.linspace(x_mm[fit.mask].min(), x_mm[fit.mask].max(), 1000)
    ax.plot(x_fit, double_slit_intensity(x_fit, fit.alpha_mm, fit.beta_mm, fit.C), "r--", label="Fit")

    ax.set_xlabel("Distance from center [mm]")
    ax.set_ylabel("Relative intensity")
    ax.grid(True)
    ax.legend(loc="upper right")
    if title:
        ax.set_title(title)

    text = (
        rf"$a$ = ({fit.a_mm:.3f} $\pm$ {fit.sigma_a_mm:.3f}) mm" "\n"
        rf"$b$ = ({fit.b_mm:.3f} $\pm$ {fit.sigma_b_mm:.3f}) mm" "\n"
        rf"$C$ = {fit.C:.3g} $\pm$ {fit.sigma_C:.2g}" "\n"
        rf"$\chi^2_{{red}}$ = {fit.chi2_red:.2f}"
    )
    ax.text(0.03, 0.95, text, ha="left", va="top", transform=ax.transAxes,
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5", alpha=0.85))
    fig.tight_layout()
    return fig, ax


def summarize_intensity_fit(fit: IntensityFitResult) -> str:
    return (
        f"alpha = ({fit.alpha_mm:.3f} +/- {fit.sigma_alpha_mm:.3f}) mm, "
        f"beta = ({fit.beta_mm:.3f} +/- {fit.sigma_beta_mm:.3f}) mm, "
        f"C = {fit.C:.3f} +/- {fit.sigma_C:.3f}\n"
        f"reduced chi^2 = {fit.chi2_red:.3f} (ndof = {fit.ndof})\n"
        f"a = ({fit.a_mm:.3f} +/- {fit.sigma_a_mm:.3f}) mm\n"
        f"b = ({fit.b_mm:.3f} +/- {fit.sigma_b_mm:.3f}) mm"
    )
