# 3D-printed single-photon diffraction

A home-built double-slit diffraction experiment in the "single-photon" regime — laser, filters, slits, and every mount that holds them — printed on a stock, budget FDM printer (Creality Ender 3), for a fraction of the cost of a lab-grade setup.

![Apparatus schematic](report/img/apparatus_schematic.png)

This started as a small physics project, later shown at a couple of student conferences. This repository is the retired, consolidated version of that work: one clean writeup instead of several conference-specific ones, and a rewritten, general-purpose analysis tool instead of the original one-off fitting scripts.

## The idea

Detecting genuine single photons needs single-photon detectors, which aren't cheap. A much cheaper stand-in: take an ordinary laser, attenuate it enormously with neutral-density filters, and let the emission statistics do the rest. A laser's photon number follows a Poisson distribution, so if the average number of photons in flight between the slit and the screen, $N$, is pushed far below 1, the odds of ever having two photons in transit at once become negligible — most "click" events really are single photons, even though the source itself is just a very dim laser.

$$N = \frac{P \cdot d \cdot \lambda}{h \cdot c^2}\cdot F_1 F_2 F_3 F_4 F_5 \qquad S = \frac{P(1)}{P(n\ge1)} = \frac{N e^{-N}}{1-e^{-N}}$$

where $P$ is the laser power, $d$ the slit-to-screen distance, $\lambda$ the wavelength, $F_1 \ldots F_5$ the transmittance of five neutral-density filters in series, and $S$ the fraction of "click" events that really are single photons. In this apparatus: a Class II laser ($P < 1$ mW), $F_1=F_2=F_3=F_4 \lesssim 0.8\%$, $F_5 \lesssim 8\%$, giving $N < 0.02$ and $S > 99\%$.

There's no single-photon detector on the other end either — instead, black-and-white photographic film, held in a 3D-printed mount, integrates the pattern over a very long exposure (hours, for the attenuated case).

## Apparatus

| | | |
|---|---|---|
| ![Laser and filter housing](report/img/apparatus.png) | ![Filter assembly](report/img/filter_assembly.png) | ![Printed double slit](report/img/double_slit.png) |
| Laser + filter housing (22 cm × 18 cm base) | One neutral-density filter, assembled | The printed double slit (5 cm × 5 cm × 0.5 cm) |

The double slit is the one component where the printer's own limits show up directly: XY resolution is set by the 0.4 mm nozzle, which bounds how narrow a slit can be printed, and the minimum slit *separation* is set by the printer's linear-guide step. Pushing past the recommended extrusion settings (hotter nozzle, closer to the bed, slower print) buys narrower slits at the cost of straightness and slit-to-slit consistency.

The film sits in its own printed mount (`report/img/film_holder.png`) at the far end of the beam path; the filters are angled inside their housing specifically to keep back-reflections from destabilizing the laser.

## Results

The width $a$ and separation $b$ of the double slit were measured three independent ways: directly under a microscope, from the minima of a clearly-visible (non-attenuated) diffraction pattern, and from a direct intensity fit of the attenuated, "single-photon" pattern.

| Method | Film | Slit width $a$ | Slit spacing $b$ |
|---|---|---|---|
| Microscope | — | $(0.12 \pm 0.03)$ mm | $(0.81 \pm 0.08)$ mm |
| High intensity, minima positions | Kentmere Pan 400, ISO 400, ~40 s | $(0.13 \pm 0.04)$ mm | $(0.8 \pm 0.2)$ mm |
| Single photon, intensity fit | Ilford Delta 3200 Professional, ISO 6400, ~8 h | $(0.15 \pm 0.01)$ mm | $(0.85 \pm 0.03)$ mm |

All three are mutually compatible. The single-photon pattern below is the same one behind the third row:

![Single-photon double-slit diffraction pattern](acquisitions/double-slit-single-photon/pattern.jpg)

Since the printer can extrude any 2D outline, not just a pair of slits, a few other apertures were tried for good measure — no quantitative fit for these, just a demonstration that the same rig produces textbook diffraction patterns for whatever shape you give it:

| Single slit | Circle | Square | Triangle |
|---|---|---|---|
| ![Single slit](acquisitions/single-slit/pattern.jpg) | ![Circular aperture](acquisitions/circle/pattern.jpg) | ![Square aperture](acquisitions/square/pattern.jpg) | ![Triangular aperture](acquisitions/triangle/pattern.jpg) |

Full derivations, apparatus details and discussion: [`report/main.pdf`](report/main.pdf) (source: `report/main.typ`; apparatus photos live in `report/img/` and are reused here directly, diffraction patterns are pulled from `acquisitions/` rather than duplicated — recompile with `typst compile --root . report/main.typ report/main.pdf` from the repository root).

## Analysis tool

[`diffraction_fit.ipynb`](diffraction_fit.ipynb) runs the fit and shows every result inline; the reusable code behind it is in [`modules/diffraction_fit.py`](modules/diffraction_fit.py). Given a scanned photo of a diffraction pattern, it:

1. extracts a 1D intensity profile through the pattern (auto-detecting the center; no manual minima-picking),
2. fits it directly against the theoretical Fraunhofer intensity,

$$I(x) = C \cos^2\!\left(\frac{\pi x}{\beta}\right)\operatorname{sinc}^2\!\left(\frac{x}{\alpha}\right) \qquad \text{(single slit: drop the } \cos^2 \text{ term)}$$

3. and converts the fitted $\alpha = \lambda D/a$, $\beta = \lambda D/b$ back into a slit width $a$ and separation $b$, with uncertainty propagated from the fit and from your wavelength/distance measurements.

```python
from diffraction_fit import analyze_diffraction_image, summarize, plot_fit

result = analyze_diffraction_image(
    "path/to/your_scan.jpg",
    pattern="double",               # or "single"
    pixel_size_mm=...,              # mm per pixel in your scan
    wavelength_nm=..., sigma_wavelength_nm=...,
    distance_mm=..., sigma_distance_mm=...,
)
print(summarize(result))
plot_fit(result)
```

Worth knowing before you point it at your own photo: this method needs the film/sensor response to be linear (unsaturated) in the region you're fitting. The notebook's own "high intensity" example was deliberately overexposed to make its minima easy to see by eye, and the fit visibly can't recover a trustworthy slit width from it — only the fringe spacing survives, since that only depends on minima *positions*. The notebook walks through this case in more detail.

### Requirements & setup

The project targets Python 3.12. The exact dependency list used in the provided dev container is in [`.devcontainer/Dockerfile`](.devcontainer/Dockerfile); the core packages are:

```
numpy scipy matplotlib pillow
jupyterlab notebook
```

Easiest path: open the repository in the provided dev container (`.devcontainer/`), which builds a ready-to-use image with everything installed and starts JupyterLab. Alternatively, install the packages above with pip in your own environment and open `diffraction_fit.ipynb`.

## Repository layout

```
modules/diffraction_fit.py   analysis code (reusable functions)
diffraction_fit.ipynb        notebook front-end, run on the images below
acquisitions/                curated scans: the 3 quantitative patterns + 3 extra geometries
stampa 3D/                   3D-printable parts
report/                      full writeup (main.typ / main.pdf), and img/ with the apparatus photos this README also uses
```

## License

Code (`modules/`, `diffraction_fit.ipynb`) is licensed under the [GNU GPLv3](LICENSE). The report (`report/`) is licensed separately under [CC BY-SA 4.0](report/LICENSE).

## References

- A. Migdall, S. V. Polyakov, J. Fan, J. C. Bienfang (eds.), *Single-Photon Generation and Detection: Physics and Applications*, Academic Press, 2013.
- E. Hecht, *Optics*, 5th edition, Pearson, 2016.
