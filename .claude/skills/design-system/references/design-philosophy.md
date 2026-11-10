# Design Philosophy: The Monolithic Engine

## 1. Creative North Star

The Creative North Star for the Andritz Precision design system is **"The Monolithic Engine."**

This is not a standard dashboard aesthetic — it is an exercise in structural weight and industrial precision. We move away from the "floating card" aesthetic of modern SaaS toward a digital architecture that feels carved from solid carbon and steel. The experience must feel like a high-end industrial command center — authoritative, dense, and technically superior.

We utilize **intentional asymmetry**: heavy data blocks anchored to a rigid left-axis while secondary metadata "floats" with generous whitespace. The contrast between technical precision and editorial layout creates a premium technical journal feel.

**Key Principles:**
- **Precision over Decoration** — Every element serves a functional purpose
- **Structural Depth** — Hierarchy is defined by material stacking, not borders
- **Monolithic Presence** — Large, bold typography creates an editorial "Blueprint" feel

## 2. The "No-Line" Rule

**EXPLICIT INSTRUCTION:** 1px solid borders for sectioning are **PROHIBITED**.

Boundaries must be defined solely through background color shifts (tonal transitions). To separate a sidebar from a main content area, use a shift from `surface` (#f8fafb) to `surface-container-low` (#f2f4f5) in light theme, or from `surface` (#10141a) to `surface-container-low` (#181c22) in dark theme.

This creates a seamless, monolithic feel rather than a "boxed-in" interface.

## 3. The "Glass & Gradient" Rule

To inject "visual soul" into the industrial framework:

- **CTA Depth:** Use a subtle linear gradient on primary buttons transitioning from `primary` (#005c97) to `primary-container` (#0075be) at a **135-degree angle**
- **Industrial Frost:** For floating navigation or modal overlays, use `surface-container-lowest` at **85% opacity** with a **20px backdrop-blur**. This keeps the data-heavy background visible but creates a clear functional layer

## 4. Tonal Architecture (Surface Hierarchy)

Treat the UI as a series of "machined plates." Depth is achieved by stacking surfaces — NOT by adding shadows.

### Light Theme Surfaces
| Token | Value | Usage |
|-------|-------|-------|
| surface | #f8fafb | Application floor |
| surface-container | #eceeef | Primary content regions |
| surface-container-low | #f2f4f5 | Sidebar/secondary sections |
| surface-container-high | #e6e8e9 | Interactive surfaces |
| surface-container-highest | #e1e3e4 | Prominent highlights |
| surface-container-lowest | #ffffff | Cards/modules for "pop" |

### Dark Theme Surfaces
| Token | Value | Usage |
|-------|-------|-------|
| surface | #10141a | Application void |
| surface-container | #1c2026 | Primary content |
| surface-container-low | #181c22 | Secondary sections |
| surface-container-high | #262a31 | Interactive surfaces |
| surface-container-highest | #31353c | Prominent highlights |
| surface-container-lowest | #0a0e14 | Deepest recesses |

A `surface-container-lowest` card sitting on a `surface-container` background provides all the separation required. No shadows needed.

## 5. Typography as Structure (Blueprint Scale)

Typography conveys industrial precision. **Inter** handles high-density data; **Gilroy** (where available) provides geometric "Monolithic" weight for headers.

- **Display (L/M/S):** 3.5rem–2.25rem — Bold only. Used for massive KPIs. Should feel like "stamped metal" — authoritative and immovable
- **Headline (L/M/S):** 2rem–1.5rem — SemiBold, tight letter-spacing (-0.02em). "Technical manual" aesthetic
- **Title (L/M/S):** 1.375rem–1rem — Medium weight. Navigation and card headers
- **Body (L/M/S):** 1rem–0.75rem — Regular weight. High-density data. Use `on-surface-variant` for secondary text
- **Label (M/S):** 0.75rem — ALL CAPS with +0.05em tracking. "Machined" look for buttons and tags

**Editorial Tip:** Pair a `display-lg` metric with a `label-sm` (all caps, +10% tracking) directly underneath to mimic an engineering technical drawing.

## 6. Elevation & Depth: Ambient Only

Shadows are atmospheric, not structural.

- **Ambient Shadow:** `0px 12px 32px 0px` — Light: `rgba(0, 28, 56, 0.06)` / Dark: `rgba(0, 28, 56, 0.4)`. Creates natural "ambient occlusion," not a dated drop shadow
- **Ghost Border Fallback:** If accessibility requires a container definition, use `outline-variant` at **15% opacity** (light) or **20% opacity** (dark). It should be "felt, not seen"
- **Dark Theme Glow:** Chart lines use `primary` (#9bcaff) with outer glow `0px 0px 8px` — "Pulse Line" effect

## 7. Data Zone Philosophy

When designing data-heavy screens:

- **NEVER shrink the text** — instead, expand the canvas
- Use `surface-container` tiers to group related data into **"Zones"**
- A Zone is a solid block of information scannable at a glance
- Zones are separated by significant **tonal shifts**, NOT lines
- This is the hallmark of a high-end, bespoke engineering tool

## 8. Industrial Aesthetic Rules

- **Sharp Corners (0px border-radius)** — NO EXCEPTIONS. Reinforces industrial precision
- **No Decorative Icons** — Every icon must accompany a functional action or status
- **ALL CAPS Labels** — Professional labeling aesthetic with +0.05em tracking
- **8px Baseline Grid** — Strict alignment, but "Hero" elements may break slightly for visual interest
- **Never Pure Black** — Use `on-secondary-fixed` (#001c38) for the deepest blacks to maintain tonal richness

## 9. Do's

- Use extreme whitespace — industrial sites are massive, the UI should feel equally expansive
- Use ALL CAPS for labels and small UI elements
- Align text to a strict baseline grid for organized "Monolithic" feel
- Allow "Hero" elements to break the 8px grid slightly for visual interest
- Use `on-surface-variant` for metadata — contrast is the primary hierarchy tool
- Pair display-lg metrics with label-sm (all caps, +10% tracking) to mimic engineering drawings

## 10. Don'ts

- **NEVER** use any border-radius — a single rounded corner breaks "Industrial Precision" logic
- **NEVER** use pure black (#000000) — use `on-secondary-fixed` (#001c38) for deepest blacks
- **NEVER** use icons as purely decorative — must accompany functional action or status
- **NEVER** use 100% opaque white borders — feels cheap and "out-of-the-box"
- **NEVER** use standard dividers — if you think you need a line, use 24px+ empty space
- **NEVER** shrink text on data-heavy screens — expand canvas and use surface-container tiers
- **DON'T** use rounded corners larger than 0px — we want "Sharp & Technical," not "Soft & Consumer"
