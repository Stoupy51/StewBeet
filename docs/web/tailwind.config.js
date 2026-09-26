/** @type {import('tailwindcss').Config} */
import plugin from 'tailwindcss/plugin';

/**
 * Every colour comes from the StewBeet logo: `ink` from the cast iron pot, `beet` from the
 * beetroot, `leaf` from its leaves. Contrast was measured against ink-950 (see
 * specs/002-website-redesign/research.md): ink-400 text is 6.8:1, beet-400 6.1:1, leaf-400 10.5:1,
 * and white on beet-600 is 5.7:1. ink-500 (3.4:1) is for boundaries only, never for text.
 *
 * Each themed shade is [dark, light]. The light column reverses the ink scale, so `text-ink-50`
 * stays the strongest text and `bg-ink-950` the page in both themes, and darkens every accent
 * used as text until it clears 4.5:1 on the light page.
 */
const THEMED = {
  ink: {
    50:  ['#f8f5f0', '#161412'],
    100: ['#eee8df', '#24211e'],
    200: ['#ddd6cc', '#353029'],
    300: ['#c4bbb0', '#4b453e'],
    400: ['#a0978c', '#615950'],
    500: ['#6e665d', '#8f867b'],
    600: ['#4b453e', '#b8afa3'],
    700: ['#353029', '#d3ccc2'],
    800: ['#24211e', '#e3ddd4'],
    850: ['#1c1a17', '#ece7e0'],
    900: ['#161412', '#fbf9f6'],
    950: ['#0e0d0c', '#f4f0ea'],
  },
  beet: {
    300: ['#ff8a99', '#9e1a33'],
    400: ['#f25c70', '#c42340'],
  },
  leaf: {
    400: ['#7fd35b', '#33701a'],
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


const channels = (hex) => [1, 3, 5].map((start) => parseInt(hex.slice(start, start + 2), 16)).join(' ');

const themedVariables = (column) => Object.fromEntries(
  Object.entries(THEMED).flatMap(([family, shades]) =>
    Object.entries(shades).map(([shade, pair]) => [`--${family}-${shade}`, channels(pair[column])])),
);

const themedColors = Object.fromEntries(
  Object.entries(THEMED).map(([family, shades]) => [family, Object.fromEntries(
    Object.keys(shades).map((shade) => [shade, `rgb(var(--${family}-${shade}) / <alpha-value>)`]),
  )]),
);

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        // Laptop screens with browser chrome: 1366x768 leaves about 650px of page.
        short: { raw: '(max-height: 760px)' },
      },
      colors: {
        ...themedColors,
        beet: { ...themedColors.beet, 500: '#e23a52', 600: '#c42340', 700: '#9e1a33', DEFAULT: themedColors.beet[400] },
        leaf: { ...themedColors.leaf, 500: '#5cb83a', DEFAULT: themedColors.leaf[400] },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans Variable"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono Variable"', 'ui-monospace', 'SFMono-Regular', 'Consolas', 'monospace'],
      },
      borderRadius: {
        panel: '8px',
        control: '6px',
      },
      maxWidth: {
        page: '72rem',
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
