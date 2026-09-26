/**
 * Class tokens shared by several components. Colours live in tailwind.config.js, named after
 * the part of the logo they come from (ink, beet, leaf).
 *
 * One accent only: beet. Filled beet is reserved for the one primary action on a screen, and a
 * hover goes darker rather than lighter, since white on beet-500 drops under 4.5:1.
 */

/** Page width and gutters, shared by every section so edges line up down the page. */
export const PAGE = 'max-w-page mx-auto px-4 sm:px-6';

/** Section title. */
export const SECTION_TITLE = 'text-[1.75rem] md:text-[2.25rem] leading-tight font-semibold tracking-tight text-ink-50 text-balance';

/** Paragraph under a section title. */
export const SECTION_LEAD = 'text-base md:text-lg text-ink-300 leading-relaxed text-pretty';

/** Heading colour for titles that set their own size. */
export const HEADING = 'text-ink-50';

/** The primary action. */
export const BTN_PRIMARY = 'inline-flex items-center justify-center gap-2 rounded-control bg-beet-600 hover:bg-beet-700 text-white font-medium transition-colors';

/** A secondary action that sits beside the primary one without competing with it. */
export const BTN_SECONDARY = 'inline-flex items-center justify-center gap-2 rounded-control border border-ink-700 bg-ink-900 hover:border-ink-500 hover:bg-ink-850 text-ink-100 font-medium transition-colors';

/** A bordered surface. */
export const CARD = 'rounded-panel border border-ink-800 bg-ink-900';

/** Hover state for a card that is a link. */
export const HOVER_CARD = 'hover:border-ink-600 hover:bg-ink-850 transition-colors';

/** Card title reacting to its card's hover. */
export const CARD_HOVER_TEXT = 'group-hover:text-beet-300 transition-colors';

/** Arrow at the end of a link card. */
export const CARD_HOVER_ARROW = 'text-xl text-ink-500 group-hover:text-beet-400 group-hover:translate-x-0.5 transition-all flex-shrink-0 mt-1';

/** Accent text. */
export const TEXT_ACCENT = 'text-beet-400';

/** Accent link. */
export const TEXT_ACCENT_HOVER = 'text-beet-400 hover:text-beet-300 transition-colors';

/** Selected row in a list or menu. */
export const LIST_SELECTED = 'bg-beet-500/15 text-beet-300';

/** Pressed state of a toggle button. */
export const TOGGLE_ACTIVE = 'bg-ink-800 border-ink-600 text-ink-50 hover:bg-ink-700';

/** Text selection colour. */
export const SELECTION_BRAND = 'selection:bg-beet-500/30 selection:text-ink-50';

/** Spinner border. */
export const LOADER_ACCENT = 'border-beet-400';
