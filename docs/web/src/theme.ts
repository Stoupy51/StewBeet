/**
 * Brand color tokens for StewBeet.
 * Primary: indigo · Secondary: purple
 *
 * To retheme the entire site, change the color values here.
 * All reusable brand UI should import from this file.
 */

/** Section heading gradient text (subtle): indigo-200 → purple-200 */
export const GRADIENT_TEXT = 'bg-gradient-to-r from-indigo-200 to-purple-200 bg-clip-text text-transparent';

/** Interactive logo gradient text (includes hover state) */
export const GRADIENT_TEXT_LOGO = 'bg-gradient-to-r from-indigo-200 to-purple-200 bg-clip-text text-transparent hover:from-indigo-300 hover:to-purple-300';

/** Page / hero title gradient (bright): indigo-400 → purple-400 → pink-400 */
export const GRADIENT_TEXT_BRIGHT = 'bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent';

/** Primary action button: indigo-600 → purple-600 gradient + shadow */
export const BTN_PRIMARY = 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/30';

/** Solid accent button for smaller actions */
export const BTN_SOLID = 'bg-indigo-600 hover:bg-indigo-700';

/** Decorative background glow blob — primary color */
export const GLOW_PRIMARY = 'bg-indigo-500/10';

/** Decorative background glow blob — secondary color */
export const GLOW_SECONDARY = 'bg-purple-500/10';

/** Navbar scrolled-state shadow */
export const NAV_SHADOW = 'shadow-indigo-500/10';

/** Active state for toggle buttons */
export const TOGGLE_ACTIVE = 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300 hover:bg-indigo-600/30';

/** Active indicator dot */
export const DOT_ACTIVE = 'bg-indigo-400';

/** Selected item in a dropdown or sidebar */
export const LIST_SELECTED = 'bg-indigo-500/20 text-indigo-300';

/** Recommended / highlighted card border + shadow */
export const CARD_HIGHLIGHT = 'border-indigo-500/50 shadow-lg shadow-indigo-500/10';

/** Interactive card hover effect */
export const HOVER_CARD = 'hover:border-indigo-500/50 hover:shadow-lg hover:shadow-indigo-500/10';

/** Shared card title hover color */
export const CARD_HOVER_TEXT = 'group-hover:text-indigo-300 transition-colors';

/** Shared card arrow hover state */
export const CARD_HOVER_ARROW = 'text-2xl text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1';

/** Brand accent text */
export const TEXT_ACCENT = 'text-indigo-400';

/** Softer accent text */
export const TEXT_ACCENT_SOFT = 'text-indigo-300';

/** Brand accent text with hover transition */
export const TEXT_ACCENT_HOVER = 'text-indigo-400 hover:text-indigo-300 transition-colors';

/** Reusable hover state for accent borders */
export const ACCENT_BORDER_HOVER = 'hover:border-indigo-500/50';

/** Accent icon color */
export const ICON_ACCENT = 'text-indigo-400';

/** Accent icon badge surface */
export const ICON_BADGE = 'bg-indigo-500/20 text-indigo-400';

/** Accent pill for small badges */
export const BRAND_PILL = 'bg-indigo-500/10 border border-indigo-500/20 text-indigo-300';

/** Accent status dot */
export const BRAND_DOT = 'bg-indigo-400';

/** Accent toolbar button surface */
export const TOOLBAR_ACCENT = 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 hover:text-indigo-300 border border-indigo-500/30';

/** Accent selection background */
export const SELECTION_BRAND = 'selection:bg-indigo-500/30';

/** Accent panel surface */
export const PANEL_ACCENT = 'bg-indigo-500/10 border border-indigo-500/20';

/** Accent alert surface */
export const ALERT_ACCENT = 'bg-indigo-500/10 border border-indigo-500/30';

/** Accent spinner border */
export const LOADER_ACCENT = 'border-indigo-500';

/** Accent input focus ring */
export const INPUT_FOCUS = 'focus:ring-indigo-500 focus:border-transparent';

/** Terminal frame glow */
export const TERMINAL_GLOW = 'bg-gradient-to-r from-indigo-500 to-purple-600';

/** Active step / tab item background */
export const STEP_ACTIVE = 'bg-indigo-500/10 border-indigo-500/50 text-white';

/** Active icon background */
export const ICON_ACTIVE = 'bg-indigo-500 text-white';

/** Active item descriptive sub-text */
export const TEXT_ACTIVE_SUBTLE = 'text-indigo-200';

/**
 * Brand-color prose overrides for @tailwindcss/typography.
 * Inject as `${PROSE_BRAND}` into article className alongside layout-only prose classes.
 */
export const PROSE_BRAND = [
    'prose-h1:bg-clip-text prose-h1:text-transparent prose-h1:bg-gradient-to-r prose-h1:from-indigo-200 prose-h1:to-purple-200',
    'prose-h2:text-indigo-100',
    'prose-a:text-indigo-400 hover:prose-a:text-indigo-300',
    'prose-code:text-indigo-300',
    'prose-li:marker:text-indigo-400',
    'prose-blockquote:border-l-indigo-500 prose-blockquote:bg-indigo-500/5',
].join(' ');
