# design.md — terminal

A design system for interfaces that look and behave like a well-riced tmux session: tiled panes, ANSI color, box-drawing, statuslines, keyboard first. The tokens drive a web UI directly (CSS below) and map one-to-one onto a 16-color terminal theme for real TUIs (§12).

**Point of view:** a mission-control HUD built by someone who lives in tmux. Dense, quiet, fast. Every color is syntax, and the eye always knows where focus is.

| reference | what this system takes from it |
|---|---|
| **A** — a urxvt/tmux session: vim, a cava spectrum, neofetch, ranger | the warm 16-color palette, tiled panes with 1px shared borders, mint active-pane border, vim and tmux statuslines, inverse-video selection, color-coded file kinds, key-in-color system info, lowercase unix voice |
| **B** — a satellite-ops dashboard | panes separated by dark gutters, hairline borders, a line-art figure as hero with callout labels, bar and segment meters, area/line charts, a log stream, a pixel display face for the one big title and numeral |

**How to apply this file.** §1 is the vocabulary; §2–§7 are the rules; §8 is the component reference, read the entry you are building; §9–§11 apply to every screen. A screen is done when every box in §13 is ticked.

---

## 1. Leading words

Six words carry the system. When something isn't covered below, decide with these.

- **Cell** — the unit of everything: one character wide by one row tall. Sizes, gaps, and positions are whole cells (half-rows allowed on the web).
- **Pane** — the only container. A rectangle with a 1px border and its title written into the top border, like a tmux pane. Panes tile; the only thing that sits over them is a popup.
- **Ink** — color is syntax highlighting. Each hue names a *kind* of thing, and each pane signs itself with one ink. Decoration gets no color.
- **Cursor** — mint means *focus*. It marks the focused pane's border, the focused control inside it, and the text caret. Focus lives in one pane at a time, so mint lives in one place at a time.
- **Inverse** — state is reverse video: a solid block of color with dark text (mode, status, selection). Foreground color says *what* a thing is; inverse says *what state* it's in.
- **Redraw** — the screen changes by redrawing. Changes are instant, or they step in discrete ticks.

Hierarchy comes from text level (bright / fg / dim), weight, and inverse. Size stays at one cell except for display numerals (§4).

---

## 2. Color

### 2.1 Tokens — the single source of truth

```css
:root {
  /* neutrals: structure and text */
  --void:   #111214; /* page background, gutters between panes */
  --bg:     #1a1b1e; /* pane surface; text color inside inverse blocks */
  --raise:  #24262a; /* statusline, hover row, inactive selection, popup */
  --line:   #34373c; /* pane borders, grid lines, separators, empty tracks */
  --dim:    #8b9096; /* context: meta, axis labels, line numbers, timestamps */
  --fg:     #c6c9c7; /* body text */
  --bright: #eef0ee; /* values, numerals, titles, selected text */

  /* inks: syntax and pane identity */
  --red:    #d4736f;
  --orange: #e0975f;
  --yellow: #ecc66f;
  --green:  #b6c06a;
  --blue:   #86a8c8;
  --purple: #b79ac4;

  /* focus and data */
  --cursor: #6fe0c0; /* focus only */
  --data:   #5fa398; /* single-series marks: bars, lines, meter fill */
  --track:  #1d3531; /* unfilled meter segments */

  /* type and grid */
  --font-text:    "Fira Mono", "JetBrains Mono", "SF Mono", Menlo, Consolas, ui-monospace, monospace;
  --font-display: "Departure Mono", "VT323", var(--font-text);
  --font-size: 14px;
  --row: 20px;                         /* one cell tall */
  --cx: calc(var(--font-size) * 0.6); /* one cell wide (0.6em monospace advance) */
}

html {
  background: var(--void);
  color: var(--fg);
  font: 400 var(--font-size) / var(--row) var(--font-text);
  font-variant-numeric: tabular-nums slashed-zero;
  font-variant-ligatures: none;
}

[data-ink="red"]    { --ink: var(--red); }
[data-ink="orange"] { --ink: var(--orange); }
[data-ink="yellow"] { --ink: var(--yellow); }
[data-ink="green"]  { --ink: var(--green); }
[data-ink="blue"]   { --ink: var(--blue); }
[data-ink="purple"] { --ink: var(--purple); }
```

Every color in code resolves to one of these tokens. Tints come from `color-mix(in srgb, var(--token) N%, transparent)` and are used for chart area fills only.

### 2.2 Roles

| role | tokens | job |
|---|---|---|
| structure | void → bg → raise, line | surfaces and borders. Elevation is one step up this ramp; depth never comes from shadow |
| text | dim, fg, bright | three levels: bright is the value, fg is the prose, dim is the context around it |
| ink | red, orange, yellow, green, blue, purple | foreground syntax (§2.3) and pane identity (§2.4) |
| cursor | cursor | focus: active pane border, focused control, caret |
| data | data, track | single-series charts and meters. Multi-series takes inks in the order blue, orange, green, purple, yellow; red is reserved for a series that *is* bad (errors, loss) |

### 2.3 Syntax table

Color says what kind a thing is, the same way in every pane, like `LS_COLORS`. Every kind also carries a non-color cue.

| kind | style | example |
|---|---|---|
| container, navigable (directory, group, section) | blue, bold, trailing `/` | `Documents/` |
| leaf content (file, media, record) | orange | `tabs.png` |
| reference (link, symlink, path, user@host) | green, `->` before a target | `PlayOnLinux Drives -> 4` |
| tag, enum, identifier | purple | `LEO`, `power_reroute` |
| keybinding | yellow | `q` |
| key in a key:value row | pane ink | `kernel:` |
| value, number | bright | `2573` |
| meta (time, size, permissions, position) | dim | `2018-05-15 11:39` |
| prose | fg | |

### 2.4 Status

Status is always a glyph plus a word. As the main state of a pane or row it's an inverse badge; inside running text it's a colored glyph followed by fg text.

| status | ink | glyph | badge |
|---|---|---|---|
| ok | green | `✓` | ` OK ` |
| live, running | green | `●` | ` ● LIVE ` |
| warn | yellow | `!` | ` WARN ` |
| err | red | `✗` | ` ERR ` |
| info | blue | `i` | ` INFO ` |

### 2.5 Ink per pane

Each pane declares one ink (`data-ink="blue"`). The ink colors the pane title, the keys of its key:value rows, its selected row (inverse), and the accent strokes of its figure. Neighboring panes take different inks; that is how a screen becomes multi-colored while every color still means something. Panes that display statuses sign with blue or purple, so the pane's identity never reads as a status.

### 2.6 Contrast (checked)

All text tokens reach at least 4.5:1 on `--bg` and `--raise`; the tightest pairs are `--red` on `--raise` (4.68) and `--dim` on `--raise` (4.71). Inverse text (`--bg` on any ink, `--dim`, `--data` or `--cursor`) reaches at least 5.3:1. `--data` on `--track` is 4.47:1, above the 3:1 needed for graphics. `--line` is structural at 1.44:1, so anything a person must perceive (focus, active pane) uses `--cursor` at 10.7:1.

---

## 3. The cell

Use `var(--cx)` for horizontal space and `var(--row)` for vertical space. These stay fixed inside display-sized elements, where `1ch` and `1lh` would drift.

| space | value | use |
|---|---|---|
| 1 cell wide | `var(--cx)` | label-to-value gap, pane inline padding, badge padding |
| 2 cells wide | `calc(var(--cx) * 2)` | between columns, between statusline segments |
| 4 cells wide | `calc(var(--cx) * 4)` | indent for nested content (tree, code) |
| half row | `calc(var(--row) / 2)` | pane block padding, gutter in the gapped layout (web only) |
| one row | `var(--row)` | between groups inside a pane |

Every list row, table row, statusline, help bar and input is exactly one row tall. Groups are separated by one empty row.

**Columns, not pixels.** Text inside a pane is at most 80 cells wide. Layouts break at column counts: four panes across at 160+ columns, two across at 80–159, one column below 80 (about 680px at 14px). In one column the panes stack in reading order, the statusline stays pinned, and the window list scrolls sideways. The layout holds at 320px.

---

## 4. Type

One monospace family carries the whole UI. A pixel display face appears at most twice per screen: the screen title and one hero numeral.

| role | face | size / line | weight |
|---|---|---|---|
| everything | `--font-text` | 14 / 20 (1 cell) | 400; 700 for titles, containers, selected rows, badges |
| display, 2× | `--font-display` | 28 / 40 (2 rows) | 400 |
| display, 3× | `--font-display` | 42 / 60 (3 rows) | 400 |

- Fira Mono is reference A's face and has no ligatures. Departure Mono (OFL, self-hosted) matches reference B's title; VT323 is the Google Fonts fallback. In a TUI, display numerals are 3-row block digits, figlet-style.
- Numerals are always tabular with a slashed zero, so columns line up and live values hold still.
- Links get a dotted underline. Nothing else is underlined; nothing is italic.
- Reference B's `TRANSMISSIØN` flourish (Ø for O) is allowed in one display title per screen, with the real word in `aria-label`.

---

## 5. Borders, glyphs, depth

- Every pane has a 1px `--line` border. The focused pane's border is `--cursor`. Corners are square everywhere: `border-radius: 0`.
- Depth is the surface ramp. Panes sit on `--void`, popups sit on `--raise`, and `box-shadow` is `none`.
- The title lives in the top border, starting one cell from the left corner, with one cell of `--bg` on each side so it cuts the line: `┌─ files ────┐`. Pane actions sit in the top-right of the border as bracketed glyphs: `[↗]`.
- Separators inside a pane are a row of `─` or a `│` column rule, in `--line`.
- Icons are glyphs from this set, sized to the cell. SVG is for figures and line charts.

| set | glyphs | use |
|---|---|---|
| box | `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ━ ╸` | borders, trees, meter bars |
| blocks | `█ ▉ ▊ ▋ ▌ ▍ ▎ ▏` | meters at eighth-cell precision; `▌` for segment meters |
| bars | `▁ ▂ ▃ ▄ ▅ ▆ ▇ █` | sparklines, spectra |
| shade | `░` | loading skeleton |
| braille | `⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏` / `⣀ ⣤ ⣶ ⣿` | spinner / dense TUI plots |
| marks | `● ○ ✓ ✗ ! › ↗ ⤢ × … ->` | status, prompts, actions, truncation, references |

Canonical pane CSS:

```css
.pane {
  position: relative;
  background: var(--bg);
  border: 1px solid var(--line);
  padding: calc(var(--row) / 2) var(--cx);
}
.pane:focus-within { border-color: var(--cursor); }
.pane-title {
  position: absolute;
  top: calc(var(--row) / -2);
  left: var(--cx);
  padding-inline: var(--cx);
  background: var(--bg);
  color: var(--ink);
  font-weight: 700;
}
```

---

## 6. Motion: redraw

- Interface state (hover, select, open, close, switch window) changes instantly: `transition: none`.
- Time-based motion steps. The caret blinks with `steps(1)` on a 1s cycle. The spinner advances one braille frame every 80ms. Meters fill a whole segment at a time. Live numbers replace in place, with no tweening.
- One optional boot moment: on the first load of a session, panes appear in reading order, 60ms apart.
- Under `prefers-reduced-motion: reduce`, the caret is solid, the spinner becomes a static `…` next to the percentage, and the boot moment is skipped.

---

## 7. Layout

A screen is one hero pane (the largest; it holds the figure or the primary content), its supporting panes, and the statusline pinned to the bottom row. A help bar may sit directly above the statusline. Text is left-aligned; numbers are right-aligned in their column.

**tiled** (default, reference A) — panes share 1px borders with zero gap and fill the viewport. For tools and dense work. Build it as a grid with `gap: 1px` over a `--line` background; the focused pane gets `outline: 1px solid var(--cursor)` and `z-index: 1` so its edges light up like tmux's active border.

```
┌─ editor ─────────────────────┬─ spectrum ──────────────────┐
│   1 batch convert            │   █        █           █    │
│   2     for i in *.mp4 …     │ █ █ █   █  █ █      █ █     │
│   3                          │ █ █ █ ▆ █ ▄█ █ ▃ ▅ ▆ █ █ ▆  │
│ NORMAL  notes.txt     1:1    │ █ █ █ █ █ ██ █ █ █ █ █ █ █  │
├─ system ─────────────────────┼─ files ─────────────────────┤
│ os:      Ubuntu 16.04        │ Art Project/            9   │
│ kernel:  x86_64 4.13         │ Desktop/                0   │
│ uptime:  9h 36m              │ Drives -> 4                 │
│ shell:   zsh 5.1.1           │ tabs.png            15.4K   │
└──────────────────────────────┴─────────────────────────────┘
 1 vim  2 music-  3:files                   thu 21 may  22:35
```

**gapped** (reference B) — each pane has its own border, separated by a `--void` gutter of half a row by one cell. For dashboards and overviews.

```
┌─ satellite ───────────────────── [⤢] ┐ ┌─ transmission ─────── [↗] ┐
│                                      │ │ packet upload        65%  │
│                                      │ │ ━━━━━━━━━━━━━━╸────────── │
│       (wireframe figure)             │ │ bandwidth quota      80%  │
│                                      │ │ ━━━━━━━━━━━━━━━━━━━╸───── │
│   ●──── hg-antenna [72%]             │ └───────────────────────────┘
│                                      │ ┌─ orbit ────┐ ┌─ battery ──┐
│                                      │ │ lat  +34.0 │ │ 90%        │
│             solar-06 [89%] ────●     │ │ lon -118.2 │ │ ▁▃▅▅▃▂▃▆█  │
│                                      │ │ (globe)    │ │ ● CHARGING │
│                                      │ │            │ │            │
└──────────────────────────────────────┘ └────────────┘ └────────────┘
┌─ SAT-0043X ─────────┐ ┌─ scanning ──────────┐ ┌─ log ──────────────┐
│ launch:  2012-03-23 │ │ solar panel 03  32% │ │ 08:32:10 reroute   │
│ orbit:   LEO        │ │ ▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌ │ │ battery temp spike │
└─────────────────────┘ └─────────────────────┘ └────────────────────┘
```

---

## 8. Components

Each entry gives the specimen, the rules, and anything state-specific. Shared states live in §9.

### 8.1 Pane

```
┌─ files ───────────────────────── [↗] ┐
│ Art Project/                       9 │
│ Desktop/                           0 │
└──────────────────────────────────────┘
```

- Props: `title` (lowercase noun), `ink`, `actions` (bracketed glyphs in the top border).
- Focused: border `--cursor`. Unfocused: border `--line`. The title stays in the pane's ink in both states.
- **Zoomed** (tmux `z`): the pane fills the layout and its window name in the statusline gains a `Z` flag.
- **Popup** (tmux `display-popup`): a pane on `--raise`, centered, at most 80 cells wide, focused on open. The panes behind stay visible and unblurred; `esc` closes it and returns focus to where it was.

### 8.2 Statusline

Two kinds, both one row on `--raise`.

```
 NORMAL  ffmpeg.txt                     unix | utf-8 | text   1%   1:1
 1 vim  2 music-  3:files                              thu 21 may  22:35
```

- **Pane statusline** (vim): a mode badge, then context (file, item) in fg; on the right, meta in dim joined by ` | `, then position blocks.
- **Session statusline** (tmux): windows on the left, the clock on the right.
- Mode badges are inverse: `VIEW`/`NORMAL` blue, `EDIT`/`INSERT` green, `SELECT`/`VISUAL` purple, `COMMAND` yellow.
- Windows act as tabs and read `index name` (index in dim). The current window reads `index:name`, bold bright text on a `--line` block. The previously visited window gets a `-` suffix, as tmux does.
- Right-hand blocks step up in brightness toward the edge: a `--line` block with fg text, then a `--dim` block with `--bg` text for the most important value. Segment ends are square.

### 8.3 List and columns

Reference A's ranger: parent, current, and preview columns.

```
affan       │ Art Project/          9 │ Donut 3D/
            │ Desktop/              0 │ Glasses/
            │ Documents/           16 │ Hand Signature/
            │ PlayOnLinux Drives -> 4 │ Skin Palette.png
            │ tabs.png          15.4K │
            │ TODO                  0 │
drwxrwxr-x  10 affan affan  2018-05-15 11:39     45M sum, 87.3G free  1/14
```

- One row per item. The name is styled by kind (§2.3); meta is right-aligned in dim.
- The selected row is the focus inside a list. In the focused pane it's inverse in the pane's ink, across the full column width. In an unfocused pane it's `--raise` with bright text.
- The parent column is dim; the preview column follows the selection.
- Long names truncate with `…` at the end and the meta stays visible. The full name shows in the footer row.
- Footer row in dim: permissions or details on the left, totals and position (`1/14`) on the right.

### 8.4 Key-value block

Reference A's neofetch and reference B's satellite card.

```
 ┌──┐ ╔══╗ ┌──┐    os:        Ubuntu 16.04 xenial
 │▒▒├─╢██╟─┤▒▒│    kernel:    x86_64 Linux 4.13.0-41
 └──┘ ╚══╝ └──┘    uptime:    9h 36m
       │           packages:  2573
```

- Keys are lowercase, end in a colon, and use the pane ink. Pad every key to the longest key plus two spaces, so values share one left edge.
- Values are fg; the single figure that matters most in the block is bright.
- At 80+ cells wide the block may run as two key:value columns separated by two cells.
- An optional figure sits to the left (§8.11).

### 8.5 Meters

**Bar** — continuous quantities.

```
packet upload                                    65%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸──────────────────
0                         125G                  210G
```

The label is fg and the value is bright and right-aligned. The fill `━` is `--data`, the tip `╸` is `--bright`, and the track `─` is `--line`. The scale row (dim) is optional.

**Segments** — discrete or scanned progress.

```
solar panel 03                     32%
▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌
```

Filled segments are `▌` in `--data`; unfilled segments are the same glyph in `--track`, so the width never shifts. `▌` leaves a natural gap between segments. The inline variant is ten segments after a percentage: `20% ▌▌▌▌▌▌▌▌▌▌`.

Markup: `role="meter"` for levels and `role="progressbar"` for tasks, with `aria-valuenow`, `aria-valuemin`, `aria-valuemax` and a label. The glyph row is `aria-hidden="true"`.

### 8.6 Charts

- **Spectrum / bar chart** (reference A's cava): vertical bars two cells wide with one-cell gaps, in `--data`. Heights snap to eighths of a row, the resolution of `▁▂▃▄▅▆▇█`. The hovered bar turns `--bright`.
- **Sparkline**: inline bar glyphs after a value, `1.6G/s ▁▂▃▅▇█▇▅`.
- **Line / area** (reference B): a 1px stroke in `--data` (or the series ink), with an area fill from `--data` at 30% down to transparent. Horizontal grid lines in `--line` sit at whole-row intervals, and the baseline is the only axis line. Axis labels are dim. Hover shows a `--dim` vertical crosshair and a `●` on the line, with the value in the pane statusline.
- **Legend**: inline, `━ download  ━ upload`, each `━` in its series ink.
- **TUI**: plot with braille, 2×4 dots per cell.

### 8.7 Badges

```
 NORMAL    ● LIVE    ✗ ERR
```

- **Solid** (inverse): modes and the primary status of a pane. Bold uppercase, one cell of padding on each side.
- **Dot**: `●` or another status glyph in ink, followed by an uppercase word in fg. For secondary status inline.

### 8.8 Buttons and actions

```
 save   [ export ]   [ cancel ]          s save   esc cancel
```

- **Default**: `[ label ]`, with brackets in dim and a lowercase verb in fg.
- **Primary**: inverse in the pane ink with no brackets. One per pane.
- **Icon action**: a bracketed glyph in the pane's top border, such as `[↗]` (expand) or `[×]` (close), with an `aria-label`.
- **Key hint**: the key in yellow, the action in dim. Every button with a shortcut shows its hint in the help bar.
- Loading: the label becomes spinner plus present participle, `⠹ saving…`, and the width holds steady.

### 8.9 Inputs

```
search:  Art Pro▌
› ffmpeg -i file.mp4▌
```

- **Field**: the label is styled as a key (pane ink, colon) and the value is fg. When focused, the row is `--raise` and the caret is a `--cursor` block (`caret-color: var(--cursor)`, plus `caret-shape: block` where supported).
- **Prompt**: `›` (or `$`, `/`, `:`) in the pane ink, for command lines and search. Placeholder text is dim and describes the input: `› filter by name`.
- **Boxed**: a three-row pane with the label in its border, for standalone fields in forms.
- A validation message sits on the row below: `✗` in red, then the message in fg (§10).
- `<label>` is bound to every input; the visible key is the label.

### 8.10 Log stream

```
2025-07-22 08:32:10  power_reroute  battery temp spike; solar input rerouted
2025-07-22 08:33:02  ✗ link_lost    ground station dropped (retrying in 30s)
── 2 new ──
```

- The timestamp is dim, the event id is purple, and the message is fg. A status glyph prefixes the id when it's needed.
- Newest entries are at the bottom. The pane follows new lines until the person scrolls up, then shows a `── n new ──` row in dim.
- `role="log"` with `aria-live="polite"`.

### 8.11 Figure and callouts

The hero. One per screen, in the largest pane.

- **ASCII art** (reference A): monospace art in fg with accent strokes in the pane ink, at most 40 cells by 20 rows.
- **Wireframe drawing** (reference B): SVG with 1px strokes in `--dim` and `--fg` and no fills except `--bg`.
- **Callout**: a `●` anchor on the figure, a 1px `--dim` leader line (straight segments, one bend at most), and a label in fg followed by its value as an inverse `--data` chip. Example: `●──── hg-antenna [72%]`.
- The figure is `aria-hidden="true"`. A visually hidden description, plus the same callout values in a list, carries its meaning.

### 8.12 Gutter and code

Reference A's vim.

```
  1 batch convert
  2     for i in *.mp4; do ffmpeg -i "$i" "${i%.mp4}.mov"; done
  3
~
~
```

Line numbers are dim and right-aligned in three cells, followed by a one-cell gap. The current line number is yellow. Rows past the end of the content show `~` in dim. Code indents by four cells.

### 8.13 Help bar

```
 q quit   / search   tab next pane   ? help
```

One row, directly above the session statusline or as a pane's last row. Keys are yellow and actions are dim, with three cells between pairs. It lists the shortcuts that work in the focused pane.

---

## 9. States

| state | treatment |
|---|---|
| hover | row or control background becomes `--raise`, instantly |
| focus | pane border becomes `--cursor`. Inside the pane, the focused row is the selection (inverse in the pane ink) and a focused control gets a 1px `--cursor` outline |
| selected, pane unfocused | `--raise` background, bright text |
| pressed | inverse `--fg` while pressed |
| disabled | label in dim, brackets and border in `--line`, no hover |
| loading | spinner plus `verb-ing thing…`, plus a percentage when known. Content areas show `░` rows in `--line` in the shape of the data that's coming |
| empty | `~` gutter rows, one line saying what belongs here, one key hint to start (§10) |
| error | the error appears in the pane where it happened. The title gains a red `✗`, and the message row uses the `ERR` pattern (§10) |
| stale | values turn dim and gain a meta note: `(stale 2m)` |
| overflow | `…` at the end of the text, meta stays visible, and the full value appears in the statusline on focus |

```
┌─ files ──────────────────────────────┐
│ ~                                    │
│ ~      no files in Art Project/      │
│ ~      n new file                    │
│ ~                                    │
└──────────────────────────────────────┘
```

---

## 10. Copy

The voice is a terse unix tool that tells you exactly what happened.

- **Case**: labels and messages are lowercase. Badges (modes and statuses) are uppercase. Real names keep their own casing: `Ubuntu`, `Art Project/`, `SAT-0043X`, `TODO`.
- **Words**: labels are nouns (`uptime`, `packet upload`). Actions are verbs that name the outcome (`save`, `delete 3 files`). An action keeps its verb through the whole flow: `save` → `saving…` → `saved ffmpeg.txt  2.4K`.
- **Numbers**: units attach without a space, in short form: `87.3G free`, `45M`, `410k`, `1.6G/s`. Durations read `9h 36m`. The clock is 24-hour, `22:35`. Dates are `2026-05-21` in data and `thu 21 may` in the statusline. Positions read `1/14`.
- **Punctuation**: ` | ` separates meta items, `:` ends a key, `->` means *points to*, `…` means truncated or in progress.
- **Errors** state what happened, then the fix in parentheses. They name the cause directly and skip apologies.

| moment | pattern | example |
|---|---|---|
| loading | verb-ing + thing + progress | `scanning solar panel 03… 32%` |
| success | past-tense verb + object + result | `saved ffmpeg.txt  2.4K` |
| error | `ERR` + what happened + (fix) | `ERR  upload stopped: connection lost (r retry)` |
| validation | `✗` + what's wrong + what's allowed | `✗ name has a slash (use letters, digits, - or _)` |
| empty | what belongs here + one key to start | `no files in Art Project/` / `n new file` |
| confirm, inline | verb + count + object + `[y/N]`, default in capitals; destructive actions default to no | `delete 3 files? [y/N]` |
| confirm, popup | the question, the consequence, buttons that repeat the verb | `delete 3 files from Videos/?` / `this can't be undone.` / `[ delete 3 files ]  [ keep ]` |
| hint | key + action | `q quit` |

---

## 11. Accessibility

- Box-drawing, ASCII art, glyph meters, spectra and sparklines are drawing laid over real semantics. Mark the drawing `aria-hidden="true"` and expose the value through a role (`meter`, `progressbar`, `img` with a label) or visually hidden text.
- Each kind and status has a non-color cue: containers are bold with a trailing `/`, references carry `->`, statuses carry a glyph and a word.
- Each pane is a `region` labelled by its title. Tab moves between panes and controls, arrow keys move within lists (roving `tabindex`), and `esc` closes popups. Single-key shortcuts fire only while focus is inside the pane that owns them, and can be remapped.
- The window list is a `tablist`. Statusline values worth announcing sit in a `role="status"` element.
- Text never goes below 14px. At 200% zoom the layout collapses to one column (§3).
- Reduced motion follows §6.

---

## 12. TUI mapping

The palette is a complete 16-color terminal theme. Inverse is SGR 7, bold is SGR 1, and a dotted link underline is SGR 4:4 where the terminal supports it.

| terminal slot | token |
|---|---|
| background | `--bg` |
| foreground | `--fg` |
| cursor | `--cursor` |
| selection background | `--raise` |
| 0 black | `--raise` |
| 8 bright black | `--dim` |
| 1 / 9 red | `--red` |
| 2 / 10 green | `--green` |
| 3 / 11 yellow | `--yellow` |
| 4 / 12 blue | `--blue` |
| 5 / 13 magenta | `--purple` |
| 6 cyan | `--data` |
| 14 bright cyan | `--cursor` |
| 7 white | `--fg` |
| 15 bright white | `--bright` |

A tmux config derived from §2.1 (update it whenever the tokens change):

```tmux
set -g pane-border-style            fg='#34373c'
set -g pane-active-border-style     fg='#6fe0c0'
set -g status-style                 bg='#24262a',fg='#8b9096'
set -g window-status-format         ' #[fg=#8b9096]#I #[fg=#c6c9c7]#W#F '
set -g window-status-current-format '#[bg=#34373c,fg=#eef0ee,bold] #I:#W '
set -g status-right                 '#[bg=#34373c,fg=#c6c9c7] %a %d %b #[bg=#8b9096,fg=#1a1b1e] %H:%M '
set -g message-style                bg='#24262a',fg='#eef0ee'
set -g mode-style                   bg='#86a8c8',fg='#1a1b1e'
```

---

## 13. Done checklist

A screen is done when every box is ticked.

- [ ] Every color in the stylesheet is a `var(--token)` from §2.1. A search for `#` or `rgb(` outside the token block finds nothing.
- [ ] Every font size is 1×, 2× or 3× the cell, and the display face appears at most twice.
- [ ] Every horizontal space is a multiple of `--cx` and every vertical space a multiple of half a `--row`. Rows are exactly one `--row` tall.
- [ ] `border-radius` is 0, `box-shadow` is none, and transitions are none or `steps()`.
- [ ] `--cursor` appears only on focus: one pane border, plus the focused control or caret inside it.
- [ ] Every pane declares an ink, and neighboring panes differ.
- [ ] Every kind and status has a non-color cue (§2.3, §2.4).
- [ ] Every interactive element has hover, focus, pressed and disabled treatments (§9).
- [ ] Every data pane has its loading, empty and error states written in the §10 patterns.
- [ ] Copy is lowercase except badges and real names, and each action keeps one verb from button to progress to result.
- [ ] The screen works at 320px wide, at 200% zoom, with the keyboard alone, and with `prefers-reduced-motion`.
