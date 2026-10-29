---
name: "ReorderIQ"
description: "A refined historical buyer review desk with inspectable prediction evidence."
colors:
  canvas: "#f5f3ed"
  surface: "#fffefa"
  surface-pure: "#fff"
  surface-soft: "#f8f7f2"
  ink: "#222e27"
  muted: "#646b61"
  subtle: "#686f64"
  rule: "#e3e5da"
  rule-strong: "#cdd2c5"
  rail: "#232e29"
  rail-text: "#eaece2"
  rail-muted: "#b7c0b3"
  rail-hover: "#2e3d34"
  rail-active: "#35493b"
  action: "#315d45"
  action-hover: "#244b35"
  selected: "#eef3e9"
  brass: "#886a3d"
  brass-light: "#dcc69d"
  brass-surface: "#f5efdf"
  danger: "#9a4134"
  danger-surface: "#f9eee8"
  track: "#e6ebdf"
  skeleton: "#e6e9df"
  dark-canvas: "#161c18"
  dark-surface: "#1e2720"
  dark-surface-pure: "#202b23"
  dark-surface-soft: "#222d24"
  dark-ink: "#edf0e6"
  dark-muted: "#b6c0af"
  dark-subtle: "#a1af9a"
  dark-rule: "#354333"
  dark-rule-strong: "#52624d"
  dark-rail: "#111a14"
  dark-rail-text: "#edf0e6"
  dark-rail-muted: "#aebba6"
  dark-rail-hover: "#223125"
  dark-rail-active: "#2d4130"
  dark-action: "#a9ccaa"
  dark-action-hover: "#c1ddbd"
  dark-selected: "#2b3b2a"
  dark-brass: "#d4bc8c"
  dark-brass-light: "#dcc69d"
  dark-brass-surface: "#3a3526"
  dark-danger: "#e3aa97"
  dark-danger-surface: "#3e2923"
  dark-track: "#3b4b35"
  dark-skeleton: "#354330"
typography:
  headline:
    fontFamily: "Instrument Serif, Georgia, serif"
    fontSize: "46px"
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: "-0.6px"
  headline-mobile:
    fontFamily: "Instrument Serif, Georgia, serif"
    fontSize: "38px"
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: "-0.4px"
  title:
    fontFamily: "Plex, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "-0.15px"
  body:
    fontFamily: "Plex, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Plex, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0.1px"
  button:
    fontFamily: "Plex, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.5
  summary:
    fontFamily: "Instrument Serif, Georgia, serif"
    fontSize: "37px"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "-0.3px"
  score:
    fontFamily: "Instrument Serif, Georgia, serif"
    fontSize: "44px"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "-1px"
  chart-axis:
    fontFamily: "Plex, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "normal"
rounded:
  panel: "10px"
  button: "6px"
  field: "5px"
  navigation: "7px"
  badge: "4px"
  tag: "3px"
  track: "2px"
  sheet-top: "16px"
spacing:
  small: "8px"
  control: "12px"
  medium: "16px"
  mobile-gutter: "18px"
  workbench: "20px"
  panel: "22px"
  large: "24px"
  section: "28px"
  gutter: "36px"
  wide-gutter: "44px"
components:
  button-primary:
    backgroundColor: "{colors.action}"
    textColor: "{colors.surface}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "11px 17px"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "11px 17px"
  button-secondary-hover:
    backgroundColor: "{colors.selected}"
  button-reveal:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "11px 18px"
  button-reveal-active:
    backgroundColor: "{colors.brass-surface}"
    textColor: "{colors.brass}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "9px 12px"
    height: "44px"
  nav-item:
    textColor: "{colors.rail-muted}"
    rounded: "{rounded.navigation}"
    padding: "12px 16px"
  nav-item-active:
    backgroundColor: "{colors.rail-active}"
    textColor: "{colors.rail-text}"
  status-tag:
    textColor: "{colors.action}"
    rounded: "{rounded.badge}"
    padding: "2px 5px"
  evidence-panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
  buyer-sheet:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    width: "calc(100% - 28px)"
---

# Design System: ReorderIQ

## Overview

**Creative North Star: "The historical review desk"**

ReorderIQ is a considered analytical desk: warm stone surrounds pale work surfaces, a deep ink-green rail anchors orientation, and restrained brass marks boundaries and attention. Instrument Serif gives headings and summary figures an editorial voice; Plex keeps controls, tables and factual context precise. The queue remains the main working artifact, paired with a buyer history inspector rather than a field of interchangeable cards.

The premium character comes from quiet material separation, deliberate type contrast and responsive continuity. Light and dark themes retain the same hierarchy and semantic assignments. Motion explains selection, navigation and the explicit transition from a historical forecast to observed outcomes; measured numbers appear directly, without animated intermediate values.

This v0.2 record is extracted from the React frontend, Vite 8 production source, Motion 14 components and supplied refinement screenshots for the local FastAPI application. It refreshes the incumbent desk. The unavailable Impeccable launcher produced no composition, FORM or QUALITYBAR artifacts; this document does not imply formal visual-world approval.

**Key Characteristics:**

- Warm stone, deep ink green and restrained brass in matching light and dark themes.
- Editorial serif headings and summary figures above compact Plex controls and data.
- Fine rules, modest rounding and diffuse surface shadows in light mode.
- A ranked buyer queue with a sticky inspector or native modal buyer sheet.
- Short, purposeful motion and explicit loading, error, empty and hidden-outcome states.

## Colors

The frontmatter records the literal CSS custom-property palette. Unprefixed tokens are light-theme values; each `dark-` counterpart replaces the same CSS property when the root has `data-theme="dark"`. Components bind to the unprefixed CSS variables so the theme changes atomically.

### Primary

- **Action green:** actions, selected-model chart lines, probability bars and observed positive states. Hover uses the action-hover companion; dark mode uses a pale green action to remain legible against ink surfaces.
- **Deep ink-green rail:** persistent navigation, with separate rail text, muted text, hover and active tones. The selected destination retains an outline and explicit current-page state.
- **Selected sage:** buyer selection, chosen-model rows and supportive positive-state backgrounds. Selection also has a textual or semantic state.

### Secondary

- **Restrained brass:** focus outlines, heading punctuation, reference chart series, buyer monograms and prediction/outcome boundary cues. Brass-light supports the rail mark and selection; brass-surface supplies the quiet outcome-reveal background.

### Neutral

- **Warm stone canvas:** the outer desk and top bar. Pale surface, surface-pure and surface-soft distinguish work areas, inset regions and table headings without a stark white dashboard.
- **Ink:** primary text and the default outcome-reveal action. Its dark-theme counterpart is a warm pale neutral.
- **Muted and subtle olive-gray:** secondary labels and placeholders. The light subtle token is the corrected legible source value; do not restore the earlier lighter value.
- **Fine and strong rules:** one-pixel dividers, surface edges and firmer field boundaries.
- **Track and skeleton:** supporting probability tracks and static loading placeholders.
- **Danger and danger-surface:** failed-request recovery and warning surfaces, with matching dark values.

**The Selection Rule.** Pair selection tint with explicit state or text; color is an additional cue.

**The Theme Parity Rule.** Keep semantic color roles identical across themes and bind components to the live CSS variables.

## Typography

**Display font:** locally bundled Instrument Serif, regular and italic, with Georgia and serif fallbacks. **Interface font:** locally hosted IBM Plex Sans, registered as Plex, with system-ui and sans-serif fallbacks; the shipped faces cover regular, medium and semibold weights. Numeric content inherits tabular numerals.

The serif carries the page title, summary values, prominent probability and editorial method/source headings. Plex carries panel titles, buyer IDs, table cells, controls and explanations. The display/interface contrast creates hierarchy without inflating every component.

- **Headline:** the frontmatter headline role; switches to headline-mobile at the mobile breakpoint. The brand uses the same serif at (29px), reduced to (26px) on mobile.
- **Title:** medium Plex panel headings. Buyer headings use (18px), growing to (21px) in the compact sheet. Method headings use regular serif (38px / 1.15), reduced to (35px) on mobile; source headings use serif (30px / 1.1).
- **Body:** the root interface role. Table and button content uses (13px); most metadata and control labels use (12px). Method prose uses (13px / 1.9), reduced to (12px / 1.95) on mobile, and caps at (70ch).
- **Label:** medium Plex form labels. Supporting metadata generally uses regular weight; reserve the label weight for actual labels or emphasis.
- **Summary:** prominent serif facts; mobile uses (31px), while hidden summary text uses italic serif (30px), reduced to (27px) on mobile.
- **Score:** the buyer probability; increases to (48px) in the mobile sheet. Its numeric value and probability label remain visible together.
- **Chart axis:** unstroked Plex text. Main evidence SVGs use (14 viewBox units), (19) at the mobile breakpoint and (21) on very narrow screens. These are SVG units, not guaranteed rendered CSS pixels. History labels use (14 SVG units) outside the sheet; the mobile sheet override uses (12).

**The Unstroked Label Rule.** Keep SVG chart text unstroked and verify its rendered reading size after responsive scaling.

**The Measured Number Rule.** Update figures directly to the measured value; motion may reveal the figure but must not invent intermediate statistics.

## Layout

The desktop shell uses a fixed rail (220px), a top bar (70px) and a centered main region with a maximum width (1650px). Default main padding is (32px 36px 22px). The workbench has four aligned columns (1.15fr 1.2fr 0.75fr auto), followed by an explicit prediction boundary and a three-part summary strip. Recurring spacing primitives are in the frontmatter; local composition also uses smaller gaps where needed.

The review area pairs a fluid queue with an inspector (320px), separated by (22px). The inspector is sticky at (22px), scrolls within `calc(100dvh - 44px)` and keeps the buyer context beside the table. The queue scrolls within a maximum height (584px); table headings remain sticky and rows are (65px) high by default. Evidence and exact-data tables contain their own horizontal overflow.

| Viewport condition | Implemented response |
| --- | --- |
| At least 1560px | Inspector becomes 355px; review gap becomes 26px; main horizontal gutters become 44px; queue maximum height becomes 650px. |
| At most 1380px | Evidence charts stack into one column with chart content capped at 860px; secondary spend columns hide in the desktop queue; controls tighten. |
| At most 1279px | Rail becomes an 82px icon rail with accessible labels and focus captions; main horizontal gutters become 28px; inspector becomes 300px. |
| At most 1100px | Review grid becomes one column and selecting a buyer opens the native modal sheet. The desktop inspector is not rendered. Queue maximum height becomes 610px; spend columns return where space allows. |
| At most 900px | Query controls become two columns; the prediction boundary wraps; spend columns hide again; method content stacks. |
| At most 720px | Brand becomes a fixed 66px top strip and navigation becomes three bottom destinations with safe-area padding. Main content uses 18px side gutters and bottom clearance; the top bar becomes 47px. Buyer, probability and outcome remain in the queue; secondary columns hide. Date, model, capacity and reveal form a compact two-column native-control layout; date steppers hide. Queue maximum height becomes 520px. |
| At most 374px | Main and topbar side gutters become 13px, export becomes an icon action and supporting chart labels increase in viewBox size. |

The compact sheet is at most (580px) wide and (88dvh) high, with width `calc(100% - 28px)` above the mobile breakpoint. On mobile it spans the viewport width. Its toolbar remains sticky while profile content scrolls. Controls keep their actual final cascade sizes: fields, theme toggle, paging and date actions use (44px) targets; bottom navigation destinations have a minimum height (52px).

**The Contained Overflow Rule.** Keep wide tables scrollable within their own containers and preserve page-width containment.

## Elevation & Depth

Depth combines warm tonal layering, fine one-pixel rules and a very diffuse light-theme panel shadow. Dark mode removes that ambient panel shadow and relies on surface separation. The buyer sheet is a deliberate raised layer with a dimmed, blurred backdrop; the mobile bottom navigation has a faint upward shadow. These are observed structural treatments, not a flat-only prohibition.

- **Panel ambient:** `0 4px 22px rgb(42 48 34 / 3%)`; dark mode resolves the same shadow token to `none`.
- **Buyer sheet:** `0 -12px 50px rgb(0 0 0 / 14%)` above a `rgb(14 23 17 / 48%)` backdrop with (3px) blur.
- **Mobile navigation:** `0 -4px 20px rgb(0 0 0 / 3%)` separates persistent navigation from scrolling content.

CSS control feedback uses (150ms) with `cubic-bezier(0.16, 1, 0.3, 1)`. Motion for React supplies the shared navigation selection (220ms, same easing), view opacity (120ms), buyer detail continuity (160ms, 5px entry), sheet continuity (200ms, 32px entry / 20px exit), explicit summary reveal (220ms, masked opacity) and selected evidence-line drawing (450ms, easeOut). None of these delay rows one by one or interpolate reported numbers.

`MotionConfig reducedMotion="user"`, `useReducedMotion` and the CSS reduced-motion query remove the spatial paths, set controlled transitions to zero, skip initial chart-line drawing and disable CSS transitions/animations. State labels, recovery actions and exact values remain available.

**The Purposeful Motion Rule.** Animate navigation, inspection and explicit outcome disclosure; keep measured values and recovery immediately usable.

## Shapes

Work surfaces use the panel radius, controls the smaller button or field radius, and navigation its own radius. Status tags and probability tracks use the smallest corners. The modal sheet rounds only its top corners using the sheet-top radius. Fine borders remain part of the material language. Small circles identify source state and individual recorded orders; outline SVG icons support labels and never substitute for chart text.

## Components

### Buttons

Precise, quiet actions with a minimum height (44px). Primary recovery actions use action green and surface text; secondary actions use a pale surface, a strong rule and ink. Hover moves to the selected surface and action border, with the primary hover companion for filled actions. Exports use a transparent surface and remain unavailable while the current query is loading, settling or failed. Disabled buttons and links use opacity (0.4) with explicit disabled semantics.

The outcome action begins in ink with surface text. Its pressed state uses brass-surface, brass text and border plus an explicit label change. Focus uses a brass outline (2px) and offset (4px); rail actions use brass-light. Paging, sheet close and theme actions use the final (44px) target size.

### Inputs / Fields

Labeled native selects and a numeric-ID search input use the frontmatter input shape, height and padding. Strong rules define rest; action color defines hover; brass defines visible keyboard focus. Search adds an inline outline icon and left padding (36px), reduced to (31px) on mobile. Placeholders use the corrected subtle token. Date selection includes desktop step controls behind a divider; the mobile date field restores native select appearance and hides steppers.

### Navigation

Three persistent destinations connect review, evidence and source. Desktop navigation uses rail-muted text and outline icons, with an inset active surface, fine outline and brass dot. The selected shape shares a Motion layout identity across destinations. The intermediate rail retains accessible destination names; mobile uses labeled bottom destinations, selected sage and action-colored text. Views and review filters persist through URL/history, and navigation places focus on the destination heading.

### Chips

Small outlined selected-model tags, quiet badges and selected-sage status tags convey information. They keep compact Plex labels and modest corners; they are not interactive filter pills. Outcome rows retain written ordered/no-order labels, and hidden outcomes have an explicit accessible name.

### Cards / Containers

Queue, buyer and evidence containers share the pale surface, fine rule, panel radius and theme-specific ambient shadow. Evidence containers clip internal content and separate heading, chart or table, and contextual footer. Padding follows the actual subregion: panel headers (21px 22px 17px), charts (0 22px 20px), buyer content (20px 22px 23px), with tighter mobile spacing. Do not apply a single generic card padding to every region.

### Buyer queue and inspector

The queue uses numeric probabilities with subordinate bars, sticky headings, selected-sage rows and explicit buyer buttons. The inspector presents a prominent probability, a prediction-cutoff note, historical facts, twelve weekly bars and recent recorded orders. Changing the query clears old evidence immediately; skeletons occupy the current request rather than presenting stale rows. Failed queue and buyer requests offer separate retry actions; empty filters offer clear recovery.

At the compact breakpoint, a native `dialog` sheet opens on buyer selection with previous/next controls. It contains Tab and Shift-Tab, closes with Escape, locks background scroll, restores the prior scroll setting and returns focus to the buyer trigger. The close action receives initial focus. All displayed buyer history stays before the selected snapshot; a date change hides later outcomes.

### Evidence charts and exact data

Selected-model performance uses a solid green line; Gamma-Poisson and reference diagonals use dashed brass. Calibration bins have equal-size points, not implied population areas. Quiet gridlines sit behind unstroked labels. Weekly inspection supports pointer movement and arrow keys with a live readout; exact weekly and calibration tables remain available. The evidence page evaluates the frozen development winner independently of the exploratory queue model. Cohort average precision stays beside purchase prevalence, and eligible-population order rates appear only after reveal.

## Do's and Don'ts

### Do:

- **Do** preserve warm stone, deep ink green and brass through live light/dark semantic variables.
- **Do** use Instrument Serif for editorial headings and prominent facts, and Plex for interface text and dense data.
- **Do** keep buyer IDs, probabilities, prediction boundaries and outcome state explicit beside graphical cues.
- **Do** retain labeled native controls, visible keyboard focus, 44px control targets and native modal focus/scroll restoration.
- **Do** keep chart labels unstroked, exact values available and wide tables contained.
- **Do** bind rows, summaries, buyer detail and exports to the successful current query, with visible loading and retry states.
- **Do** respect reduced motion while preserving labels, measured values and outcome-disclosure meaning.

### Don't:

- **Don't** replace numeric probabilities or written outcome states with color-only or bar-only encodings.
- **Don't** animate statistics through invented intermediate values or use row-by-row entrance delays.
- **Don't** render stale responses or export a prior query as current evidence.
- **Don't** restore the earlier low-contrast subtle text color or inherit outline-icon stroke into SVG chart text.
- **Don't** force the desktop inspector, icon rail or two-column evidence charts below their observed breakpoints.
- **Don't** imply that purchase propensity measures the causal effect of contact, or present illustrative component previews as experiment data.
