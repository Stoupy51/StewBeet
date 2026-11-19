/** @type {import('tailwindcss').Config} */
import plugin from 'tailwindcss/plugin';

/**
 * Every value here comes from DESIGN.md, which also says where each colour may be used. A themed
 * colour is [dark, light] and becomes a CSS variable on :root, switched by `data-theme`.
 *
 * `ink`, `beet` and `leaf` are the scales the pages not yet redesigned are built on, set to the
 * same neutrals so they match the redesigned ones. The light column reverses the ink scale, so
 * `text-ink-50` stays the strongest text and `bg-ink-950` the page in both themes.
 */
const THEMED = {
  surface: ['#0c0d0f', '#ffffff'],
  text: ['#f2f3f5', '#111214'],
  'text-muted': ['#a3a7b0', '#565964'],
  border: ['#272930', '#e3e4e8'],
  link: ['#ff6b7d', '#b81d39'],
  generated: ['#7fd35b', '#2b7a19'],
  'code-surface': ['#15171b', '#ffffff'],
  'code-border': ['#2a2d34', '#e3e4e8'],
  'code-text': ['#e6e7ea', '#1f2328'],
  'code-text-muted': ['#9aa0aa', '#565964'],
  'section-start': ['#63d96b', '#1f7a2a'],
  'section-guides': ['#7c9cff', '#3045c0'],
  'section-plugins': ['#f0b23c', '#8a5a00'],
  'section-reference': ['#d98cf0', '#8b2fa3'],
  'section-understand': ['#5fd3e0', '#0b6f7a'],
};

const THEMED_SCALES = {
  ink: {
    50:  ['#f2f3f5', '#111214'],
    100: ['#e2e4e8', '#1d1e22'],
    200: ['#cdd0d6', '#2c2e33'],
    300: ['#b8bcc4', '#3d4047'],
    400: ['#a3a7b0', '#565964'],
    500: ['#6b6f78', '#8a8d96'],
    600: ['#4a4d55', '#b4b7be'],
    700: ['#383b42', '#d0d2d7'],
    800: ['#272930', '#e3e4e8'],
    850: ['#1b1d21', '#eeeff1'],
    900: ['#141518', '#f7f7f8'],
    950: ['#0c0d0f', '#ffffff'],
  },
  beet: {
    300: ['#ff8a99', '#9e1a33'],
    400: ['#ff6b7d', '#b81d39'],
  },
  leaf: {
    400: ['#7fd35b', '#2b7a19'],
  },
  mc: {
    gold:   ['#f2c14e', '#94670a'],
    copper: ['#d0795a', '#a8481f'],
  },
  sky: {
    300: ['#7dd3fc', '#0369a1'],
  },
  red: {
    200: ['#fecaca', '#991b1b'],
    300: ['#fca5a5', '#b91c1c'],
    900: ['#7f1d1d', '#fee2e2'],
  },
  amber: {
    200: ['#fde68a', '#92400e'],
    400: ['#fbbf24', '#b45309'],
  },
  emerald: {
    300: ['#6ee7b7', '#047857'],
  },
  green: {
    300: ['#86efac', '#15803d'],
    900: ['#14532d', '#dcfce7'],
  },
};

/** The 16 px grid drawn in the page margins, too faint to need its alpha changed through Tailwind. */
const GRID = ['rgba(255, 255, 255, 0.06)', 'rgba(17, 18, 20, 0.07)'];

const channels = (hex) => [1, 3, 5].map((start) => parseInt(hex.slice(start, start + 2), 16)).join(' ');

const PAIRS = {
  ...THEMED,
  ...Object.fromEntries(Object.entries(THEMED_SCALES).flatMap(([family, shades]) =>
    Object.entries(shades).map(([shade, pair]) => [`${family}-${shade}`, pair]))),
};

const themedVariables = (column) => ({
  ...Object.fromEntries(Object.entries(PAIRS).map(([name, pair]) => [`--${name}`, channels(pair[column])])),
  '--grid': GRID[column],
});

const variable = (name) => `rgb(var(--${name}) / <alpha-value>)`;

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    // Square everywhere, avatars excepted.
    borderRadius: {
      none: '0px',
      DEFAULT: '0px',
      panel: '0px',
      control: '0px',
      full: '9999px',
    },
    extend: {
      screens: {
        // Laptop screens with browser chrome: 1366x768 leaves about 650px of page.
        short: { raw: '(max-height: 760px)' },
      },
      colors: {
        ...Object.fromEntries(Object.keys(THEMED).map((name) => [name, variable(name)])),
        primary: '#c42340',
        'primary-hover': '#9e1a33',
        'on-primary': '#ffffff',
        'mc-panel': '#c6c6c6',
        'mc-slot': '#8b8b8b',
        'mc-tooltip': '#100010',
        'mc-tooltip-border': '#5000ff',
        'mc-lore': '#cc66dd',
        ...Object.fromEntries(Object.entries(THEMED_SCALES).map(([family, shades]) => [family, Object.fromEntries(
          Object.keys(shades).map((shade) => [shade, variable(`${family}-${shade}`)]),
        )])),
        beet: { 300: variable('beet-300'), 400: variable('beet-400'), 500: '#e23a52', 600: '#c42340', 700: '#9e1a33', DEFAULT: variable('beet-400') },
        leaf: { 400: variable('leaf-400'), 500: '#5cb83a', DEFAULT: variable('leaf-400') },
      },
      fontFamily: {
        sans: ['"Archivo Variable"', 'Archivo', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono Variable"', 'ui-monospace', 'SFMono-Regular', 'Consolas', 'monospace'],
        pixel: ['Monocraft', '"JetBrains Mono Variable"', 'monospace'],
      },
      maxWidth: {
        page: '75rem',
      },
    },
  },
  plugins: [
    plugin(({ addBase }) => addBase({
      // `.code-dark` keeps code panels dark in both themes: the highlighting is VS Code's dark-plus.
      ':root, .code-dark': { ...themedVariables(0), colorScheme: 'dark' },
      ':root[data-theme="light"]': { ...themedVariables(1), colorScheme: 'light' },
    })),
  ],
}
