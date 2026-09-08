"""
Fraunhofer single/double-slit diffraction analysis.

Turns a scanned photo of a diffraction pattern into a fitted slit width
(and, for a double slit, slit separation), by extracting a 1D intensity
profile through the pattern and fitting it directly against the
theoretical Fraunhofer intensity:

    single slit:  I(x) = C * sinc(x / alpha)^2
    double slit:  I(x) = C * cos(pi x / beta)^2 * sinc(x / alpha)^2

where `alpha` is the position of the first diffraction minimum (alpha =
lambda * D / a) and `beta` is the spacing between interference minima
(beta = lambda * D / b), with `a` the slit width, `b` the slit
separation, `lambda` the laser wavelength and `D` the slit-to-screen
distance. `x` is the distance from the pattern center.

No minima need to be picked by hand: `curve_fit` is run on the whole
profile at once.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


# --------------------------------------------------------------------------
# Profile extraction
# --------------------------------------------------------------------------

def load_grayscale(image_path: str) -> np.ndarray:
    """Load an image as a float grayscale array."""
    return np.asarray(Image.open(image_path).convert("L"), dtype=float)


def extract_intensity_profile(
    gray: np.ndarray,
    center_y_px: int | None = None,
    band_height_px: int | None = None,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """
    Average a horizontal band of the image into a 1D intensity profile.

    Intensity is taken as `255 - grayscale` (film exposure darkens the
    film, so more exposure = darker pixel = higher intensity).

    `center_y_px` (the row the diffraction streak is centered on) and
    `band_height_px` are auto-detected when not given: the center row is
    the one with the highest total intensity, and the band height
    defaults to 2% of the image height.
    """
    h, w = gray.shape
    intensity_img = 255.0 - gray

    if band_height_px is None:
        band_height_px = max(8, round(0.02 * h))

    if center_y_px is None:
        row_totals = intensity_img.sum(axis=1)
        center_y_px = int(np.argmax(row_totals))

    y1 = max(0, center_y_px - band_height_px // 2)
    y2 = min(h, center_y_px + band_height_px // 2)
    band = intensity_img[y1:y2, :]

    profile = band.mean(axis=0)
    profile_std = band.std(axis=0)
    return profile, profile_std, center_y_px, band_height_px


def estimate_center_x_px(profile: np.ndarray) -> float:
    """Intensity-weighted centroid, restricted to the bright core of the
    profile so background noise away from the pattern doesn't bias it."""
    x = np.arange(len(profile))
    mask = profile >= 0.5 * profile.max()
    return float(np.sum(x[mask] * profile[mask]) / np.sum(profile[mask]))


# --------------------------------------------------------------------------
# Theoretical models
# --------------------------------------------------------------------------

def single_slit_model(x, alpha, C):
    return C * np.sinc(x / alpha) ** 2


def double_slit_model(x, alpha, beta, C):
    return C * np.cos(np.pi * x / beta) ** 2 * np.sinc(x / alpha) ** 2


_MODELS = {"single": single_slit_model, "double": double_slit_model}


# --------------------------------------------------------------------------
# Fit
# --------------------------------------------------------------------------

@dataclass
class FitResult:
    pattern: str
    popt: np.ndarray
    perr: np.ndarray
    chi2_red: float
    ndof: int
    mask: np.ndarray
    param_names: list[str] = field(default_factory=list)

    def __getitem__(self, name: str) -> tuple[float, float]:
        i = self.param_names.index(name)
        return float(self.popt[i]), float(self.perr[i])


def _initial_guess(x_included: np.ndarray, y_included: np.ndarray, pattern: str) -> list[float]:
    """Envelope-aware initial guess. A plain "half the included x-range"
    estimate for alpha fails on wide, many-fringed patterns, where
    secondary lobes still poke above the intensity threshold far from
    the center: it reports the whole visible range instead of the
    central lobe's width. Instead, find the fringe peaks and use the
    span of the *tall* ones (the central lobe) for alpha, and their
    spacing for beta."""
    peaks, _ = find_peaks(y_included, prominence=0.05 * y_included.max())

    if len(peaks) == 0:
        fallback = float((x_included.max() - x_included.min()) / 4) or 1.0
        return [fallback, fallback / 6, 1.0] if pattern == "double" else [fallback, 1.0]

    peak_x, peak_y = x_included[peaks], y_included[peaks]
    strong = peak_x[peak_y >= 0.3 * peak_y.max()]
    alpha0 = float((strong.max() - strong.min()) / 2) if len(strong) > 1 else float(np.abs(peak_x).max())
    alpha0 = alpha0 or 1.0

    if pattern == "single":
        return [alpha0, 1.0]

    beta0 = float(np.median(np.diff(peak_x))) if len(peaks) >= 2 else alpha0 / 6
    return [alpha0, beta0, 1.0]


def fit_profile(
    x_mm: np.ndarray,
    intensity: np.ndarray,
    intensity_err: np.ndarray,
    pattern: str = "double",
    intensity_threshold: float = 0.1,
    fit_window: float | None = None,
    p0: list[float] | None = None,
) -> FitResult:
    """Fit a normalized intensity profile (peak ~1) to the chosen model.

    Points below `intensity_threshold` (fraction of the peak) are
    excluded, matching the low-signal cutoff used in the original
    analysis (film grain noise dominates there).

    `fit_window` optionally restricts the fit to `|x| <= fit_window`
    (same unit as `x_mm`). Real slits aren't perfectly rectangular, and
    on a pattern wide enough to show several diffraction lobes, the far
    lobes can visibly depart from the ideal sinc^2 envelope; since they
    also outnumber the central-lobe points, an unweighted whole-profile
    fit gets pulled towards them and misjudges the envelope width. The
    original hand-picked-minima method sidestepped this by only trusting
    cleanly visible minima; restricting the fit window is the equivalent
    move for a whole-profile fit.
    """
    if pattern not in _MODELS:
        raise ValueError(f"pattern must be one of {list(_MODELS)}, got {pattern!r}")
    model = _MODELS[pattern]
    param_names = ["alpha", "beta", "C"] if pattern == "double" else ["alpha", "C"]

    mask = intensity >= intensity_threshold
    if fit_window is not None:
        mask &= np.abs(x_mm) <= fit_window
    x_fit, y_fit, sigma_fit = x_mm[mask], intensity[mask], intensity_err[mask]
    sigma_fit = np.where(sigma_fit > 0, sigma_fit, np.nanmedian(sigma_fit[sigma_fit > 0]) or 1.0)

    if p0 is None:
        p0 = _initial_guess(x_fit, y_fit, pattern)

    lower = [1e-6] * (len(param_names) - 1) + [1e-9]
    popt, pcov = curve_fit(
        model, x_fit, y_fit, p0=p0, sigma=sigma_fit, absolute_sigma=True,
        bounds=(lower, np.inf), maxfev=20000,
    )
    perr = np.sqrt(np.diag(pcov))

    residuals = (y_fit - model(x_fit, *popt)) / sigma_fit
    chi2 = float(np.sum(residuals ** 2))
    ndof = len(x_fit) - len(popt)

    return FitResult(pattern, popt, perr, chi2 / ndof, ndof, mask, param_names)


# --------------------------------------------------------------------------
# Physical slit size / spacing, with propagated uncertainty
# --------------------------------------------------------------------------

def physical_length(
    param_mm: float, sigma_param_mm: float,
    wavelength_nm: float, sigma_wavelength_nm: float,
    distance_mm: float, sigma_distance_mm: float,
) -> tuple[float, float]:
    """Convert a fitted alpha/beta [mm] into a slit width/spacing [mm]
    via length = lambda * D / param, propagating the three relative
    uncertainties in quadrature (covariances between lambda, D and the
    fit parameter are neglected, as in the original analysis)."""
    length_mm = (wavelength_nm * 1e-6) * distance_mm / param_mm
    rel_err = np.sqrt(
        (sigma_wavelength_nm / wavelength_nm) ** 2
        + (sigma_distance_mm / distance_mm) ** 2
        + (sigma_param_mm / param_mm) ** 2
    )
    return length_mm, length_mm * rel_err


# --------------------------------------------------------------------------
# High-level pipeline
# --------------------------------------------------------------------------

@dataclass
class DiffractionAnalysis:
    image_path: str
    x_mm: np.ndarray
    intensity: np.ndarray
    intensity_err: np.ndarray
    center_x_px: float
    center_y_px: int
    fit: FitResult
    slit_width_mm: tuple[float, float] | None = None
    slit_spacing_mm: tuple[float, float] | None = None


def analyze_diffraction_image(
    image_path: str,
    pattern: str = "double",
    pixel_size_mm: float | None = None,
    wavelength_nm: float = 520.0,
    sigma_wavelength_nm: float = 15.0,
    distance_mm: float | None = None,
    sigma_distance_mm: float = 0.0,
    center_x_px: float | None = None,
    center_y_px: int | None = None,
    band_height_px: int | None = None,
    intensity_threshold: float = 0.1,
    fit_window_mm: float | None = None,
    p0: list[float] | None = None,
) -> DiffractionAnalysis:
    """
    Run the full pipeline on one image: extract the intensity profile,
    auto-center it, fit it to the Fraunhofer model, and (if
    `pixel_size_mm` and `distance_mm` are given) convert the fit into a
    physical slit width / spacing.

    If `pixel_size_mm` is omitted, the profile stays in raw pixels
    (`x_mm` is then really "x_px") — useful to try the tool on an image
    you haven't calibrated yet.
    """
    gray = load_grayscale(image_path)
    profile, profile_std, center_y_px, _ = extract_intensity_profile(
        gray, center_y_px=center_y_px, band_height_px=band_height_px
    )

    if center_x_px is None:
        center_x_px = estimate_center_x_px(profile)

    scale = pixel_size_mm if pixel_size_mm is not None else 1.0
    x_mm = (np.arange(len(profile)) - center_x_px) * scale

    peak = float(np.interp(center_x_px, np.arange(len(profile)), profile))
    intensity = profile / peak
    intensity_err = profile_std / peak

    fit = fit_profile(x_mm, intensity, intensity_err, pattern, intensity_threshold, fit_window_mm, p0)

    result = DiffractionAnalysis(
        image_path, x_mm, intensity, intensity_err, center_x_px, center_y_px, fit
    )

    if pixel_size_mm is not None and distance_mm is not None:
        alpha_mm, sigma_alpha_mm = fit["alpha"]
        result.slit_width_mm = physical_length(
            alpha_mm, sigma_alpha_mm, wavelength_nm, sigma_wavelength_nm,
            distance_mm, sigma_distance_mm,
        )
        if pattern == "double":
            beta_mm, sigma_beta_mm = fit["beta"]
            result.slit_spacing_mm = physical_length(
                beta_mm, sigma_beta_mm, wavelength_nm, sigma_wavelength_nm,
                distance_mm, sigma_distance_mm,
            )

    return result


def save_profile_csv(result: DiffractionAnalysis, csv_path: str) -> None:
    """Dump the extracted profile (not just the fit plot) to a CSV, so
    results aren't locked inside a matplotlib figure."""
    x_unit = "x_mm" if result.slit_width_mm or result.slit_spacing_mm else "x_px"
    header = f"{x_unit},intensity,intensity_err"
    data = np.column_stack([result.x_mm, result.intensity, result.intensity_err])
    np.savetxt(csv_path, data, delimiter=",", header=header, comments="", fmt="%.6g")


def plot_fit(result: DiffractionAnalysis, title: str | None = None):
    """Data + fit overlay + a parameter text box, mirroring the plots in
    the original (unpublished) analysis scripts this tool replaces."""
    model = _MODELS[result.fit.pattern]
    x, y, yerr = result.x_mm, result.intensity, result.intensity_err
    x_unit = "mm" if result.slit_width_mm or result.slit_spacing_mm else "px (uncalibrated)"

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, "-k", label="Data")
    ax.fill_between(x, y - yerr, y + yerr, color="orange", alpha=0.3, label="Error")

    x_fit = np.linspace(x[result.fit.mask].min(), x[result.fit.mask].max(), 1000)
    ax.plot(x_fit, model(x_fit, *result.fit.popt), "r--", label="Fit")

    ax.set_xlabel(f"Distance from center [{x_unit}]")
    ax.set_ylabel("Relative intensity")
    ax.grid(True)
    ax.legend(loc="upper right")
    if title:
        ax.set_title(title)

    text_lines = [rf"${name}$ = {v:.3g} $\pm$ {e:.2g}" for name, (v, e) in
                  ((n, result.fit[n]) for n in result.fit.param_names)]
    text_lines.append(rf"$\chi^2_{{red}}$ = {result.fit.chi2_red:.2f}")
    if result.slit_width_mm:
        text_lines.append(rf"$a$ = ({result.slit_width_mm[0]:.3f} $\pm$ {result.slit_width_mm[1]:.3f}) mm")
    if result.slit_spacing_mm:
        text_lines.append(rf"$b$ = ({result.slit_spacing_mm[0]:.3f} $\pm$ {result.slit_spacing_mm[1]:.3f}) mm")

    ax.text(
        0.03, 0.95, "\n".join(text_lines), ha="left", va="top", transform=ax.transAxes,
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5", alpha=0.85),
    )
    fig.tight_layout()
    return fig, ax


def summarize(result: DiffractionAnalysis) -> str:
    """Human-readable summary of a `DiffractionAnalysis`, in the same
    spirit as the console output of the original scripts."""
    lines = [f"Image: {result.image_path}", f"Pattern: {result.fit.pattern}-slit"]
    for name in result.fit.param_names:
        value, err = result.fit[name]
        lines.append(f"  {name} = {value:.4g} +/- {err:.2g}")
    lines.append(f"  reduced chi^2 = {result.fit.chi2_red:.3f} (ndof = {result.fit.ndof})")
    if result.slit_width_mm:
        lines.append(f"Slit width a  = ({result.slit_width_mm[0]:.3f} +/- {result.slit_width_mm[1]:.3f}) mm")
    if result.slit_spacing_mm:
        lines.append(f"Slit spacing b = ({result.slit_spacing_mm[0]:.3f} +/- {result.slit_spacing_mm[1]:.3f}) mm")
    return "\n".join(lines)
