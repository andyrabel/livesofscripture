# Stained-glass portrait master prompt

## Scope

This document defines the canonical generation prompt and acceptance criteria
for portraits stored in `images/portraits2`.

Use this prompt verbatim for the `images/portraits2` series. Replace only the
three bracketed values: `[BIBLE CHARACTER]`, `[DISPLAY NAME]`, and
`[SYMBOLS / SCENE DETAILS]`.

When a Tabernacle-period priest is depicted wearing the priestly breastplate,
the scene details must require exactly twelve distinct gemstones in four
horizontal rows of three, following Exodus 28:17–20. Treat any other gem count
or arrangement as a material failure that requires correction.

```text
Use case: historical-scene
Asset type: 1024 × 1024 square website portrait
Primary request: Create a convincingly authentic late-19th-century or early-20th-century Victorian Gothic Revival church stained-glass window depicting [BIBLE CHARACTER].
Subject and story symbols: One central full or three-quarter-length [BIBLE CHARACTER], immediately recognizable, with historically appropriate ancient Near Eastern clothing, appearance, hair, and accessories. [SYMBOLS / SCENE DETAILS] No other prominent person.
Style/medium: A real handcrafted stained-glass window photographed installed in an old church, not a digital painting or a stained-glass filter. Construct the entire scene from individually shaped pieces of colored glass separated by prominent dark lead came lines. Include irregular glass shapes, subtle variations in glass thickness and translucency, tiny imperfections, fine painted details on the serious, dignified, expressive face and hands, and realistic light glowing through the glass.
Framing: Centered and balanced, character filling most of the square window, with a large rounded or Gothic arch, symmetrical architectural framing, and decorative floral and geometric border pieces around all four edges. Keep the character clearly dominant. Background imagery must also be constructed from stained glass and lead lines.
Palette: Rich traditional ecclesiastical colors—deep cobalt and sapphire blue, ruby and burgundy red, amber, antique gold, cream, muted green, brown, and occasional turquoise—luminous but slightly aged, never neon.
Text (verbatim): "[DISPLAY NAME]"
Text placement: At the bottom, incorporate an elegant antique cream-colored stained-glass name panel framed in gold and dark lead. Write only [DISPLAY NAME] in large, clear, traditional black serif capitals.
Constraints: exact square composition; one central figure; strong black leading; intricate handcrafted glasswork; realistic transmitted light; elaborate Victorian and Gothic Revival craftsmanship; dignified biblical realism; historically evocative; convincingly resemble a photograph or extremely faithful reproduction of an actual historic stained-glass Bible window installed in an old church.
Avoid: any other text, misspelling, extra words, multiple unrelated scenes, modern illustration, cartoon style, anime, glossy 3D rendering, photorealistic human photography, smooth digital gradients, plastic-looking glass, modern clothing, modern objects, excessive halos unless traditionally appropriate, illegible lettering, or watermark.
```

Generation mode: Codex built-in image generation, one distinct call per person.
Final format: PNG, normalized to exactly 1024 × 1024 pixels.
