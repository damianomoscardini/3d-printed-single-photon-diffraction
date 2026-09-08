#set document(title: "3D-Printed Single-Photon Diffraction", author: "Damiano Moscardini")
#set page(paper: "a4", margin: (x: 2.5cm, y: 2.5cm), numbering: "1")
#set text(font: "New Computer Modern", size: 11pt, lang: "en")
#set heading(numbering: "1.1")
#set par(justify: true, leading: 0.65em)

#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(0.5em)
  text(size: 18pt, weight: "bold", it)
  v(0.8em)
}

#show raw: set text(font: "DejaVu Sans Mono", size: 9.5pt)

#align(center, [
  #set par(justify: false)
  #text(size: 20pt, weight: "bold", "3D-Printed \"Single-Photon\" Double-Slit Diffraction")

  #v(0.8em)
  #text(size: 12pt, "Damiano Moscardini") \
  #text(size: 10pt, "Pisa, Italy")

  #v(1.5em)
  #link("https://creativecommons.org/licenses/by-sa/4.0/")[
    #image("img/cc-by-sa.svg", height: 1.1cm)
  ]
])

#v(1.5em)
// ------------------------------------------------------------
= Introduction

FDM 3D printing makes it possible to prototype and build inexpensive, easy-to-use experimental apparatus. This project replicates, using entirely home-printed components, a double-slit diffraction experiment operated in the "single-photon" regime — a version of Young's experiment that carries particular historical and conceptual weight, since observing an interference pattern build up one detection event at a time is one of the clearest demonstrations that light is neither a classical wave nor a classical stream of particles.

Detecting genuine single photons needs single-photon detectors, which are neither cheap nor simple. The approach here is narrower and much cheaper: attenuate an ordinary laser enormously with neutral-density filters and let Poisson statistics do the rest, so that "clicks" (in this case, grains of exposed film) are, with better than 99% probability, individually due to single photons. The apparatus — laser mount, filter housing, double slit, and film holder — is entirely 3D-printed in PLA on a stock, unmodified Creality Ender 3, aside from the glass/optical filters themselves. This report does not claim to demonstrate anything new about quantum optics; the result is methodological: this experiment, historically performed with specialized laboratory equipment, is reachable with a consumer 3D printer, off-the-shelf optical filters, and photographic film, at a small fraction of the usual cost.

= Experimental apparatus

#figure(
  image("img/apparatus_schematic.png", width: 95%),
  caption: [Schematic of the apparatus: laser, five neutral-density filters $F_1 .. F_5$ (angled to avoid back-reflection into the laser cavity — a straight-through arrangement was found to destabilize the laser's output), double slit, and photographic film at distance $D$. Each dot on the film represents one detection event; the pattern is built up one grain at a time over the exposure.],
)

The beam from a Class II laser (Quarton VLM-520-52-LPT, wavelength $lambda = (520 plus.minus 15)$ nm, power $P < 1$ mW) passes through a stack of up to five neutral-density filters $F_1$ through $F_5$, each individually characterized with a photodiode and a multimeter so its transmission coefficient is known. In this apparatus $F_1 = F_2 = F_3 = F_4 lt.eq 0.8%$ and $F_5 lt.eq 8%$, so the full five-filter stack (used for the single-photon exposure) has a combined transmittance of order $F_1 F_2 F_3 F_4 F_5 approx 3 times 10^(-10)$; a partial stack of just $F_1, F_2$ (used for the brighter, non-attenuated exposure) transmits of order $0.8% times 0.8% approx 6 times 10^(-5)$. The attenuated beam then passes through a 3D-printed double slit, and the resulting diffraction pattern is recorded on black-and-white photographic film held in a 3D-printed mount at a distance $D$ of a few meters.

#figure(
  image("img/apparatus.png", width: 65%),
  caption: [The laser and filter housing. The wooden base measures 22 cm #sym.times 18 cm. All structural parts are 3D-printed; only the laser diode itself and the glass neutral-density filters are not.],
)

#grid(
  columns: (1fr, 1fr),
  gutter: 1.5em,
  figure(image("img/filter_assembly.png", width: 100%), caption: [One neutral-density filter, fully assembled and disassembled: the printed container (with magnets for attaching the lid), the lid, and the assembled filter with the laser passing through it. Each filter's case measures 5 cm #sym.times 5 cm #sym.times 0.5 cm.]),
  figure(image("img/film_holder.png", width: 100%), caption: [The film holder: the mount that positions the photographic film at distance $D$ from the slit and keeps it flat during the (sometimes hours-long) exposure. Its wooden base measures 11 cm #sym.times 33 cm.]),
)

== The double slit

#grid(
  columns: (1fr, 1fr),
  gutter: 1.5em,
  figure(image("img/double_slit.png", width: 100%), caption: [The double slit actually used in the experiment. The whole printed part measures 5 cm #sym.times 5 cm #sym.times 0.5 cm.]),
  figure(image("img/slit_definition.png", width: 78%), caption: [Definition of the slit width $a$ and slit separation $b$ used throughout this report.]),
)

=== Fabrication constraints

The double slit is the one component where the printer's own limitations show up directly in the physics. Its resolution in the horizontal (X-Y) plane is set by the diameter of the nozzle, 0.4 mm, which is therefore the theoretical lower bound on the printable slit width $a$. Narrower slits can be coaxed out of the printer by raising the nozzle temperature above the filament's recommended setting, lowering the nozzle closer to the print bed, and slowing the print down — all of which let the extruded plastic spread out slightly more than it normally would. This works, but at a cost: the resulting slits are noticeably less straight and less identical to one another than slits printed at the recommended settings, which is reflected in the comparatively large uncertainty on $a$ in the results below. The minimum slit *separation* $b$, by contrast, is set by the minimum step of the printer's linear guides, independent of the nozzle: in this apparatus, that minimum step is what determined the smallest achievable value of $b$.

= The single-photon regime

An attenuated laser is not a true single-photon source: the number of photons it emits in any given interval follows a Poisson distribution,
$ P(n) = frac(N^n e^(-N), n!), $
where $N$ is the mean number of photons simultaneously in flight between the slit and the screen. $N$ can be written as the mean energy delivered per transit time, divided by the energy of a single photon, times the total filter transmittance:
$ N = frac(P dot Delta t, h nu) dot T_"tot" = frac(P dot (D\/c), h c \/ lambda) dot T_"tot" = frac(P dot D dot lambda, h dot c^2) dot T_"tot", quad T_"tot" = F_1 F_2 F_3 F_4 F_5, $
with $P$ the laser power, $D$ the slit-to-screen distance, $lambda$ the wavelength, $h$ Planck's constant and $c$ the speed of light. Plugging in this apparatus's numbers — $P < 1$ mW, $D approx 4$ m, $lambda < 535$ nm, $T_"tot" approx 4 times 10^(-9)$ (four filters engaged), $h approx 6.6 times 10^(-34)$ J#sym.dot.op s, $c approx 2.99 times 10^8$ m/s — gives $N < 0.02$.

When $N lt.double 1$, the probability of two or more photons being in flight at the same time becomes negligible, so almost every detection event corresponds to a genuinely single photon. Precisely, the fraction of "click" events (at least one photon arriving) that are single-photon events is
$ S(N) = frac(P(1), P(n gt.eq 1)) = frac(P(1), 1 - P(0)) = frac(N e^(-N), 1 - e^(-N)). $
With $N < 0.02$ this gives $S > 99%$: strictly speaking this is not a single-photon source, hence the quotation marks used throughout, but under these conditions it is a very good approximation of one. Since there is no affordable single-photon detector on the receiving end either, the "detector" is ordinary black-and-white photographic film, which integrates the arriving photons over a very long exposure — the single-photon pattern in this report was built up over roughly eight hours, one photon at a time, in exactly the same way the historical single-photon interference experiments were performed with photomultipliers decades ago.

= Method: two independent film analyses <method>

The width $a$ and separation $b$ of the double slit were determined three independent ways: directly under a microscope, from a deliberately *non-attenuated* exposure clear enough to pick out individual diffraction minima by eye, and from the *attenuated*, single-photon-regime exposure. The two film-based methods use different analysis strategies, for a physical reason worth making explicit.

The non-attenuated exposure (Kentmere Pan 400 film, developed at an effective ISO of 400, exposed for about 40 s, with only $F_1 = F_2 lt.eq 0.8%$ engaged and $D = (4021 plus.minus 5)$ mm) was deliberately overexposed to make the fringes easy to see by eye — which saturates the film's response near the pattern's center, so the recorded optical density stops tracking the true light intensity there. Fitting the *positions* of the diffraction minima against fringe order sidesteps this entirely, since a minimum's location does not depend on how saturated the peaks around it are. Writing $x_"diff"(n)$ for the position of the $n$-th diffraction (envelope) minimum and $x_"int"(n)$ for the position of the $n$-th interference minimum,
$ x_"diff" (n) = frac(lambda D, a) dot n, quad x_"int"(n) = frac(lambda D, b) dot (n + 1/2), $
so a straight-line fit of minimum position against order directly gives $lambda D \/ a$ and $lambda D \/ b$ as its slopes. Equivalently, in terms of the position of the first diffraction minimum $Y$ and the spacing between adjacent interference minima $Delta y$,
$ a = frac(lambda D, Y), quad b = frac(lambda D, Delta y). $
For this exposure, $Y = (17 plus.minus 2)$ mm and $Delta y = (2.6 plus.minus 0.3)$ mm.

The attenuated, single-photon exposure (Ilford Delta 3200 Professional film, push-processed to an effective ISO of 6400, exposed for about 8 hours, with the full five-filter stack engaged and $D = (4091 plus.minus 5)$ mm) was built up slowly enough to stay within the film's linear response range, so its *whole intensity profile* can instead be fit directly against the theoretical pattern shape, with no minima-picking needed — indeed, without strong attenuation the pattern would saturate just as the first exposure did, so working in the single-photon regime is not just conceptually motivated but also technically convenient here. For a double slit of width $a$ and separation $b$, observed at distance $D$, the Fraunhofer intensity as a function of position $x$ from the pattern's center is
$ I(x) = C dot cos^2!(frac(pi b x, lambda D)) dot op("sinc")^2!(frac(pi a x, lambda D)) = C dot cos^2!(frac(pi x, beta)) dot op("sinc")^2!(frac(x, alpha)), quad alpha = frac(lambda D, a), quad beta = frac(lambda D, b), $
with $C$ an overall scale. $alpha$ and $beta$ (and hence $a$ and $b$) are obtained with a nonlinear least-squares fit of this function to the measured intensity profile.

The third measurement, with a microscope, is a direct geometric measurement of the printed slit and needs no optical model.

The repository accompanying this report includes cleaned-up, English versions of the code behind both fits, as two self-contained scripts: `high_intensity_fit.py` and `single_photon_fit.py`, reproducing the results below.

= Results

#figure(
  table(
    columns: (auto, auto, auto, auto),
    align: (left, left, center, center),
    stroke: 0.5pt,
    [*Method*], [*Film / conditions*], [*Slit width* $a$], [*Slit spacing* $b$],
    [Microscope], [direct measurement], [$(0.12 plus.minus 0.03)$ mm], [$(0.81 plus.minus 0.08)$ mm],
    [High intensity, minima positions], [Kentmere Pan 400, ISO 400; $T approx 40$ s; $F_1 = F_2 lt.eq 0.8%$; $D = (4021 plus.minus 5)$ mm], [$(0.13 plus.minus 0.04)$ mm], [$(0.8 plus.minus 0.2)$ mm],
    [Single photon, intensity fit], [Ilford Delta 3200, ISO 6400; $T approx 8$ h; $F_1..F_4 lt.eq 0.8%$, $F_5 lt.eq 8%$; $D = (4091 plus.minus 5)$ mm], [$(0.15 plus.minus 0.01)$ mm], [$(0.85 plus.minus 0.03)$ mm],
  ),
  caption: [Slit width $a$ and spacing $b$, measured three independent ways. All three are mutually compatible within their uncertainties.],
)

#figure(
  image("/acquisitions/double-slit/pattern.jpg", width: 100%),
  caption: [Non-attenuated ("high intensity") double-slit diffraction pattern. Kentmere Pan 400 film, developed at ISO 400, exposed for $T approx 40$ s. Only filters $F_1 = F_2 lt.eq 0.8%$ were used; $D = (4021 plus.minus 5)$ mm. Deliberately overexposed to make the minima easy to pick out by eye — see @method for why this rules out a direct intensity fit for this particular image.],
)

#figure(
  image("/acquisitions/double-slit-single-photon/pattern.jpg", width: 100%),
  caption: [Double-slit diffraction pattern in the "single-photon" regime ($N < 0.02$, $S > 99%$). Ilford Delta 3200 Professional film, push-processed to an effective ISO of 6400, exposed for $T approx 8$ h with all five filters engaged ($F_1 = F_2 = F_3 = F_4 lt.eq 0.8%$, $F_5 lt.eq 8%$); $D = (4091 plus.minus 5)$ mm. Each dark grain corresponds, with better than 99% confidence, to a single detected photon; the pattern above is the accumulation of the whole 8-hour exposure.],
)

== Additional geometries

An FDM printer can extrude any 2D outline, not just a pair of rectangular slits. A few other apertures were printed and photographed for good measure — purely illustrative, with no quantitative fit attempted for these — and all show the qualitatively expected diffraction pattern for their shape:

#figure(
  image("/acquisitions/single-slit/pattern.jpg", width: 100%),
  caption: [Single slit, $D approx 4$ m.],
)

#grid(
  columns: (1fr, 1fr),
  gutter: 1.5em,
  figure(image("/acquisitions/circle/pattern.jpg", width: 100%), caption: [Circular aperture (Airy pattern), $D approx 5$ m.]),
  figure(image("/acquisitions/square/pattern.jpg", width: 100%), caption: [Square aperture, $D approx 2.4$ m.]),
)
#figure(
  image("/acquisitions/triangle/pattern.jpg", width: 60%),
  caption: [Triangular aperture, $D approx 2.4$ m.],
)

= Conclusion

This project does not demonstrate anything new in single-photon optics — the underlying physics is a century old, and the "single-photon" source used here is an approximation built on Poisson statistics, not a true single-photon emitter. The point was to reason the way physicists reasoned when these experiments were first performed, and to check, end to end, whether the apparatus itself could be built with a consumer 3D printer instead of specialized lab equipment. It can: the double slit's width and separation, measured three independent ways (microscope, non-attenuated pattern, single-photon pattern), agree with each other, and the same rig, given differently-shaped printed apertures, readily produces textbook diffraction patterns for those shapes too.

= References

Migdall, A., Polyakov, S. V., Fan, J., Bienfang, J. C. (eds.). _Single-Photon Generation and Detection: Physics and Applications_. Academic Press, 2013.

Hecht, E. _Optics_. 5th edition, Pearson, 2016.
