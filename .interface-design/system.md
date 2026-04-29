# DjangoBlog Interface Design System

## Intent

**Who:** Developer-bloggers and their readers. The author is a Chinese developer sharing technical knowledge. Readers arrive to read long-form technical articles, browse by tag or category, and occasionally comment.

**What they must do:** Read comfortably. Find articles by topic. Navigate between posts. The secondary persona (the author) publishes and manages content via Django Admin.

**How it should feel:** Editorial minimalism. Like a well-typeset technical journal — precise, unhurried, nothing decorative. Words on a clean surface. Typography leads; structure disappears.

---

## Color System

### Semantic Tokens (CSS Variables → Tailwind)

| Role | Light | Dark | Tailwind |
|---|---|---|---|
| Background | `rgb(249 250 251)` gray-50 | `rgb(15 23 42)` slate-900 | `bg-background` |
| Foreground | `rgb(17 24 39)` | `rgb(226 232 240)` slate-200 | `text-foreground` |
| Card | `rgb(255 255 255)` | `rgb(30 41 59)` slate-800 | `bg-card` |
| Border | `rgb(229 231 235)` | `rgb(51 65 85)` slate-700 | `border-border` |
| Muted bg | `rgb(243 244 246)` | `rgb(51 65 85)` | `bg-muted` |
| Muted text | `rgb(107 114 128)` | `rgb(148 163 184)` slate-400 | `text-muted-foreground` |
| Secondary bg | `rgb(243 244 246)` | `rgb(51 65 85)` | `bg-secondary` |
| Primary | Theme-dependent (CSS var) | — | `text-primary` / `bg-primary` |

### Multi-Theme Primary Colors

The primary color is user-configurable via `data-color-scheme` on `<body>`. Default is **purple** (`--color-primary-500: 168 85 247`). Other schemes: `blue`, `green`, `orange`, `pink`, `red`, `indigo`, `teal`.

**Always use `text-primary`, `bg-primary`, `border-primary` — never hardcode a color.**

Primary opacity modifiers in use:
- `bg-primary/5` — active nav background
- `bg-primary/8` — tag cloud prominent items
- `bg-primary/10` — category badge bg, tag hover bg
- `bg-primary/20` — category badge hover bg
- `border-primary/30` — tag cloud prominent border
- `border-primary/40` — search input focus border

---

## Typography

**Font stack:** `Open Sans`, `Helvetica Neue`, `Helvetica`, `Arial`, `sans-serif`
**Mono:** `Consolas`, `Monaco`, `Courier New`, `monospace`
**Base size:** 16px, `line-height: 1.75` (reading-optimized)
**Heading line-height:** 1.25

### Text Hierarchy

| Level | Classes | Use |
|---|---|---|
| Primary | `text-foreground font-bold` | Titles, headings |
| Body | `text-foreground` | Article body, card titles |
| Secondary | `text-muted-foreground` | Metadata, dates, view counts |
| Micro | `text-[11px] text-muted-foreground` | Timestamps, counts in sidebar |

### Heading Scale in UI

- Page/article title: `text-2xl md:text-3xl font-bold tracking-tight`
- Section heading (list page): `text-xl font-bold`
- Card title: `text-xl sm:text-2xl font-bold leading-snug tracking-tight`
- Sidebar section: `text-sm font-semibold tracking-tight`

---

## Depth Strategy

**Approach: Borders + shadow-sm**
Cards use `border border-border` for definition and `shadow-sm` for a whisper of lift. No decorative shadows. The nav uses `backdrop-blur-xl` for the frosted glass effect.

- Cards/panels: `rounded-xl border border-border bg-card shadow-sm`
- Dropdowns: `rounded-xl border border-border bg-card shadow-xl shadow-foreground/5`
- Nav: `border-b border-border/60 bg-background/80 backdrop-blur-xl`
- Footer: `border-t border-border/60 bg-muted/30`

**Rule:** Never add heavy shadows. `shadow-xl` is reserved for elevated overlays (dropdowns, modals).

---

## Layout

### Page Container
```
mx-auto max-w-6xl px-4 py-4 lg:px-6 lg:py-6
```

### Two-Column Grid (all content pages)
```
grid gap-6 lg:grid-cols-[1fr_300px]
```
- Main content: left column
- Sidebar desktop: `hidden lg:block` → `sticky top-20`
- Sidebar mobile: `mt-8 lg:hidden` → `details` accordion

### Responsive Breakpoints
- `lg` (1024px) — sidebar shows, sidebar accordion hides
- `md` (768px) — footer switches to row layout
- `sm` (640px) — article card stats row

---

## Component Patterns

### Card
```
rounded-xl border border-border bg-card shadow-sm
```
- List article: `p-4`
- Detail article wrapper: `overflow-hidden rounded-xl border border-border bg-card shadow-sm`
- Detail article inner: `p-6 md:p-8`
- Sidebar widgets: `p-5`

### Category Badge
```
inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary
hover:bg-primary/20
```

### Tag Pill (article card footer)
```
inline-flex items-center rounded-md border border-border px-2 py-0.5 text-xs font-normal text-foreground/70
hover:border-primary hover:bg-primary/10 hover:text-primary
```

### Tag Cloud (sidebar) — size-weighted
```
inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5
hover:border-primary hover:bg-primary/10 hover:text-primary
  [large]:  border-primary/30 bg-primary/8 text-foreground text-sm font-semibold  (size >= 18)
  [medium]: border-border text-foreground text-sm                                  (size >= 13)
  [small]:  border-border/60 text-muted-foreground text-xs                        (size < 13)
```

### Interactive Link / Nav Item (hover state)
```
hover:bg-secondary hover:text-primary   (for list items, sidebar links)
hover:bg-secondary hover:text-foreground  (for nav items — softer)
```

### Active Nav Item
```
text-primary bg-primary/5
+ <span class="absolute bottom-0 left-1/2 h-0.5 w-4 -translate-x-1/2 rounded-full bg-primary">
```
The 4px underline pill is the **signature mark** — typographic precision.

### Social Icon Button (footer)
```
flex size-8 items-center justify-center rounded-lg bg-secondary text-muted-foreground
hover:bg-primary hover:text-primary-foreground
```

### Search Input (inline, nav)
```
h-9 w-44 rounded-lg border border-border bg-secondary/60 px-3
focus-within:w-56 focus-within:border-primary/40 focus-within:bg-background focus-within:ring-2 focus-within:ring-primary/20
```

---

## Spacing Base Unit

**4px (Tailwind's default 1 unit)**

Key multiples in use:
- `gap-1.5` (6px) — tight gaps (tags, icon+text)
- `gap-2` / `gap-2.5` (8px/10px) — metadata rows
- `gap-3` (12px) — sidebar list items
- `gap-4` (16px) — sidebar section header to content
- `gap-5` (20px) — article list cards
- `gap-6` (24px) — grid column gap, major sections
- `p-4` (16px) — card padding (compact)
- `p-5` (20px) — sidebar widget padding
- `p-6 md:p-8` — article detail padding

---

## Border Radius Scale

| Use | Class |
|---|---|
| Inline badge/pill | `rounded-full` |
| Tag pill, inputs, buttons, nav items | `rounded-lg` |
| Cards, sidebars, dropdowns | `rounded-xl` |
| Avatar | `rounded-full` |

---

## Icon System

**Library:** Heroicons (outline style, stroke-width 2)
**Sizes:**
- `size-3` — inline metadata icons
- `size-3.5` — chevron in dropdowns
- `size-4` — sidebar section icons, nav button icons
- `size-[18px]` — nav icon buttons (theme toggle, hamburger)

**Primary color icons** (semantic emphasis): sidebar section headers (`text-primary`)
**Muted icons**: metadata rows (`text-muted-foreground`)

---

## Animation

- Nav dropdown: `ease-out duration-150` / `ease-in duration-100`
- Mobile nav: `ease-out duration-200` / `ease-in duration-150`
- Back-to-top: `ease-out duration-300`
- Lightbox: `ease-out duration-300` / `ease-in duration-200`
- Hover transitions: `transition-colors duration-200`

**Rule:** Fast micro-interactions. No bounce/spring. Deceleration easing on enter.

---

## Dark Mode

- Toggled via `data-theme="dark"` on `<html>` + `.dark` class
- Flash prevention: inline script in `<head>` reads `localStorage` before CSS loads
- Dark surfaces use Slate scale (not pure black)
- Shadows increase opacity in dark mode

---

## Tech Stack

- **Tailwind CSS** (v3, with `@tailwindcss/typography` plugin)
- **Alpine.js** — all interactive state (nav dropdowns, mobile menu, lightbox, back-to-top)
- **HTMX** — SPA-style navigation (`hx-boost`, `hx-target="#main"`)
- **Django template tags** — `{% load blog_tags %}`, `{% load_sidebar %}`, `{% load_article_detail %}`
- **Vite** — frontend bundler (`{% vite_js 'src/main.js' %}`)

---

## Rules

1. **No inline `style` attributes.** Everything via Tailwind classes.
2. **No JS hover handlers** (`onmouseenter`/`onmouseleave`). Use `hover:` utilities.
3. **No hardcoded hex colors.** Always use semantic tokens (`text-primary`, `bg-card`, etc.).
4. **One accent color only.** `primary` is the sole accent. Never introduce a second.
5. **Borders before shadows.** Define structure with `border-border`, add `shadow-sm` only for lift.
6. **Primary opacity modifiers** for tinted surfaces, not solid `bg-primary` fills (except on active icon buttons in footer).
