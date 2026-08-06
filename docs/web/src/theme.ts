/**
 * Brand tokens for StewBeet.
 * Primary: mc-emerald · Warm accent: mc-copper · Info accent: mc-diamond
 *
 * The palette is defined in tailwind.config.js and named after the blocks it comes from.
 * To retheme the site, change the values there; nothing here hardcodes a colour.
 *
 * Two rules hold this together:
 *   - Headings are solid, never gradient. Gradient text is reserved for the single hero
 *     line it is meant to emphasise; applied to every heading it stops being emphasis.
 *   - The primary button is bright emerald with near-black text (10.9:1) rather than a
 *     colour gradient with white text (which measured 1.8:1 on its light end).
 */

/** Section headings. Solid, high contrast, no gradient. */
export const HEADING = 'text-slate-50';

/** Sub-headings inside a section. */
export const HEADING_SOFT = 'text-slate-200';

/** Interactive logo text. */
export const LOGO_TEXT = 'text-slate-50 hover:text-mc-emerald transition-colors';

/** The one gradient on the site: the hero's second line. */
export const GRADIENT_TEXT_BRIGHT = 'bg-gradient-to-r from-mc-emerald via-mc-diamond to-mc-gold bg-clip-text text-transparent';

/** Primary action button: bright emerald, near-black label. */
export const BTN_PRIMARY = 'bg-mc-emerald hover:bg-mc-diamond text-slate-950 shadow-lg shadow-mc-emerald/20';

/** Solid accent button for smaller actions. */
export const BTN_SOLID = 'bg-mc-emerald hover:bg-mc-diamond text-slate-950';

/** Secondary button: outlined, sits beside the primary without competing with it. */
export const BTN_SECONDARY = 'border border-white/15 hover:border-mc-emerald/60 text-slate-200 hover:text-white';

/** Crisp 4px divider that replaces the blurred glow blobs between sections. */
export const PIXEL_RULE = 'h-1 w-full bg-pixel-rule opacity-60';

/** The single decorative glow the site still uses, in the hero only. */
export const GLOW_PRIMARY = 'bg-mc-emerald/10';

/** Navbar scrolled-state shadow. */
export const NAV_SHADOW = 'shadow-black/40';

/** Active state for toggle buttons. */
export const TOGGLE_ACTIVE = 'bg-mc-emerald/15 border-mc-emerald/50 text-mc-emerald hover:bg-mc-emerald/25';

/** Active indicator dot. */
export const DOT_ACTIVE = 'bg-mc-emerald';

/** Selected item in a dropdown or sidebar. */
export const LIST_SELECTED = 'bg-mc-emerald/15 text-mc-emerald';

/** Recommended / highlighted card border. */
export const CARD_HIGHLIGHT = 'border-mc-emerald/50 shadow-lg shadow-mc-emerald/10';

/** Interactive card hover effect. */
export const HOVER_CARD = 'hover:border-mc-emerald/50 hover:shadow-lg hover:shadow-mc-emerald/10';

/** Shared card title hover colour. */
export const CARD_HOVER_TEXT = 'group-hover:text-mc-emerald transition-colors';

/** Shared card arrow hover state. */
export const CARD_HOVER_ARROW = 'text-2xl text-slate-400 group-hover:text-mc-emerald group-hover:translate-x-1 transition-all flex-shrink-0 mt-1';

/** Brand accent text. */
export const TEXT_ACCENT = 'text-mc-emerald';

/** Softer accent text. */
export const TEXT_ACCENT_SOFT = 'text-mc-diamond';

/** Brand accent text with hover transition. */
export const TEXT_ACCENT_HOVER = 'text-mc-emerald hover:text-mc-diamond transition-colors';

/** Reusable hover state for accent borders. */
export const ACCENT_BORDER_HOVER = 'hover:border-mc-emerald/50';

/** Accent icon colour. */
export const ICON_ACCENT = 'text-mc-emerald';

/** Accent icon badge surface. */
export const ICON_BADGE = 'bg-mc-emerald/15 text-mc-emerald';

/** Accent pill for small badges. */
export const BRAND_PILL = 'bg-mc-emerald/10 border border-mc-emerald/25 text-mc-emerald';

/** Accent status dot. */
export const BRAND_DOT = 'bg-mc-emerald';

/** Accent toolbar button surface. */
export const TOOLBAR_ACCENT = 'bg-mc-emerald/10 hover:bg-mc-emerald/20 text-mc-emerald hover:text-mc-diamond border border-mc-emerald/30';

/** Accent selection background. */
export const SELECTION_BRAND = 'selection:bg-mc-emerald/30 selection:text-white';

/** Accent panel surface. */
export const PANEL_ACCENT = 'bg-mc-emerald/10 border border-mc-emerald/25';

/** Accent alert surface. */
export const ALERT_ACCENT = 'bg-mc-copper/10 border border-mc-copper/30';

/** Accent spinner border. */
export const LOADER_ACCENT = 'border-mc-emerald';

/** Accent input focus ring. */
export const INPUT_FOCUS = 'focus:ring-mc-emerald focus:border-transparent';

/** Terminal frame glow. */
export const TERMINAL_GLOW = 'bg-mc-emerald';

/** Active step / tab item background. */
export const STEP_ACTIVE = 'bg-mc-emerald/10 border-mc-emerald/50 text-white';

/** Active icon background. */
export const ICON_ACTIVE = 'bg-mc-emerald text-slate-950';

/** Active item descriptive sub-text. */
export const TEXT_ACTIVE_SUBTLE = 'text-mc-diamond';

/**
 * Brand-colour prose overrides for @tailwindcss/typography.
 * Inject as `${PROSE_BRAND}` into article className alongside layout-only prose classes.
 */
export const PROSE_BRAND = [
    'prose-h1:text-slate-50',
    'prose-h2:text-slate-100',
    'prose-a:text-mc-emerald hover:prose-a:text-mc-diamond',
    'prose-code:text-mc-diamond',
    // prose-code wins over prose-a, so `[`ruby.png`](url)` rendered as ordinary code
    '[&_a_code]:text-mc-emerald [&_a_code]:underline [&_a_code]:underline-offset-2',
    'hover:[&_a_code]:text-mc-diamond',
    'prose-li:marker:text-mc-emerald',
    'prose-blockquote:border-l-mc-emerald prose-blockquote:bg-mc-emerald/5',
].join(' ');
