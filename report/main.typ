#set document(title: "3D-Printed Single-Photon Diffraction", author: "Damiano Moscardini")
#set page(paper: "a4", margin: (x: 2.5cm, y: 2.5cm), numbering: "1")
#set text(font: "New Computer Modern", size: 11pt, lang: "en")
#set heading(numbering: "1.1")
#set par(justify: true, leading: 0.65em)
#set math.equation(numbering: "(1)")
#let munit(val, unit) = [#val\u{202F}#unit] // #munit("0.4", "mm")

#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(0.5em)
  text(size: 18pt, weight: "bold", it)
  v(0.8em)
}

#show raw: set text(font: "DejaVu Sans Mono", size: 9.5pt)

#align(center, [
  #set par(justify: false)
  #v(9cm)
  #text(size: 20pt, weight: "bold", "3D-Printed \"Single-Photon\" Diffraction Experiment")

  #v(1cm)
  #text(size: 12pt, "Damiano Moscardini") \
  #text(size: 10pt, "Pisa, Italy")

  #v(9cm)
  #link("https://creativecommons.org/licenses/by-sa/4.0/")[
    #image("img/cc-by-sa.svg", width: 1.4cm)
  ]
  #v(0.2em)
  #text(size: 8pt)[
    This report is licensed under a #link("https://creativecommons.org/licenses/by-sa/4.0/")[CC BY-SA 4.0] license.
  ]
])

#v(1.5em)
// ------------------------------------------------------------
= Introduction

FDM 3D printing makes it possible to prototype and build inexpensive, easy-to-use experimental apparatus. This project replicates, using home-printed components, a double-slit diffraction experiment operated in the "single-photon" regime — a version of Young's experiment that carries particular historical and conceptual weight.

= Experimental setup

== Light source

#figure(
  image("img/apparatus_schematic.png", width: 95%),
  caption: [Schematic of the apparatus.],
) <apparatus_schematic_figure>

The experimental setup is shown in @apparatus_schematic_figure. A #munit(5, "V") green laser (model: Quarton VLM-520-52-LPT) emits light with a wavelength of $lambda = #munit($(520 plus.minus 15)$, "nm")$ . The beam passes through a series of five neutral density filters, labeled F1 to F5, with each label indicating its transmission coefficient, measurable with a photodiode and a multimeter. The assembly of one filter is shown in Figure 3. The filters are angled with respect to the beam direction, in order to avoid back-reflection into the laser cavity. The total transmittance of the filters combined, $T_"tot"$ is given by the product of the transmittance of each filter,

$ T_"tot" = F_1 dot F_2 dot F_3 dot F_4 dot F_5. $

#figure(
  image("img/apparatus.png", width: 100%),
  caption: [Photograph of the light source. The wooden base measures #munit(22, "cm") #sym.times #munit(18, "cm"). The mounting base has holes for screws that fix it to the wooden base and allow the height to be adjusted correctly; inside, further holes hold neodymium magnets (#munit(10, "mm") diameter, #munit(3, "mm") height) that keep the lid in place during acquisition.],
) <apparatus_figure>

#figure(
  image("img/filter_assembly.png", width: 100%), 
  caption: [One neutral-density filter, fully assembled and disassembled: the printed container (with magnets for attaching the lid), the lid, and the assembled filter with the laser passing through it. Each filter's case measures #munit(5, "cm") #sym.times #munit(5, "cm") #sym.times #munit(5, "cm").],
)

A double-slit is placed after the filters, and the resulting diffraction pattern is recorded on a screen at distance $D$. The average number of photons simultaneously present between the slit and the screen in a single travel, N is given by

$ N = frac(E_"laser", E_gamma) dot T_"tot" = frac(P dot Delta t, h dot nu) dot T_"tot" = frac(P dot frac(D, c), h dot frac(c, lambda)) dot T_"tot" = frac(P dot D dot lambda, h dot c^2) dot T_"tot", $

where $P$ is the laser power, $h$ is Planck's constant and $c$ is the speed of light. In this experiment, $P < #munit("1", "mW")$ (the laser is classified as Class II), $D < #munit("5", "m")$ (the size of the room where the experiment was performed), $F_1 = F_2 = F_3 = F_4 <= #munit("0.8", "%")$ and $F_5 <= #munit("8", "%")$, yielding $N < 0.02$ under these conditions.

== How to get a "single-photon"

An attenuated laser *is not* a single-photon source,
as the number of photons it emits follows a Poisson
distribution [1]. However, when the light intensity is
reduced such that $N << 1$, the probability of having
two or more photons in the same travel becomes
negligible. The fraction of single-photon events
among all events where at least one photon is
emitted, $S$ is given by

$ S(N) = frac(P(1), P(n gt.eq 1)) = frac(P(1), 1 - P(0)) = frac(N e^(-N), 1 - e^(-N)), $

where $P$ is the probability of having $n$ photons per transit, given by the Poisson distribution. if $N < 0.02$, a value of $S > #munit("99", "%")$ is obtained.

== How to detect a "single-photon"

To maintain the experiment's affordability, single-photon detectors were not considered. Instead, a photographic film was used, being held in place by a 3D printed mount, as shown in Figure 4.

#figure(
  image("img/film_holder.png", width: 100%), 
  caption: [The film holder: the mount that positions the photographic film at distance $D$ from the slit and keeps it flat during the (sometimes hours-long) exposure. Its wooden base measures 11 cm #sym.times 33 cm.]
)

The holder also has holes for screws, so it can be fixed to the work surface and aligned with the rest of the apparatus. Its front section is detachable: a small block with 0.4 mm tall tabs that the film slides into and is held flat by, with four magnets on its back that let it snap onto the vertical back plate. The film itself is not magnetic — only the block it slides into is. This split matters because the film has to be unpacked, unrolled, cut to size, and slid into the block in complete darkness before the laser can be switched on, which is very difficult to do by touch alone. With the room lit, the back plate is positioned and fixed to the work surface, aligned with the rest of the apparatus; the lights are then turned off, the film is unpacked and slid into the front block, and the block is snapped back onto the back plate by its own magnets — the film only has to be handled by touch, while the magnets make sure everything lands back in the correct position.

== Fabrication of the double slit

The 3D printer used was a stock Creality Ender 3, with a resolution in the horizontal (X-Y) plane set by the #munit(0.4, "mm") nozzle diameter, which sets the theoretical minimum slit width. Narrower slits can be achieved with careful tuning, such as raising the nozzle temperature above the filament's recommended setting, lowering the nozzle closer to the print bed, and slowing the print down — all of which let the extruded plastic spread out slightly more than it normally would. This works, but at a cost: the resulting slits are noticeably less straight and less identical to one another than slits printed at the recommended settings, which is reflected in the comparatively large uncertainty on $a$ in the results below. The minimum slit *separation* $b$, by contrast, is set by the minimum step of the printer's linear guides, independent of the nozzle: in this apparatus, that minimum step is what determined the smallest achievable value of $b$.

#figure(
  grid(
    columns: (1fr, 1fr),
    gutter: 1em,
    image("img/double_slit.jpg", width: 90%),
    image("img/double_slit_iso.png", width: 82%),
  ),
  caption: [The double slit actually used in the experiment. The whole printed part measures #munit(5, "cm") #sym.times #munit(5, "cm") #sym.times #munit(0.5, "cm").],
)

= Method: two independent film analyses <method>

The width $a$ and separation $b$ of the double slit were determined three independent ways: directly under a microscope, from a *non-attenuated* exposure clear enough to pick out individual diffraction minima, and from the *attenuated*, single-photon-regime exposure. The two film-based methods use different analysis strategies, for a physical reason worth making explicit.

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

[1] Migdall, A., Polyakov, S. V., Fan, J., Bienfang, J. C. (eds.). _Single-Photon Generation and Detection: Physics and Applications_. Academic Press, 2013.

[2] Hecht, E. _Optics_. 5th edition, Pearson, 2016.
