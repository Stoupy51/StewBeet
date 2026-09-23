/** @type {import('tailwindcss').Config} */

/**
 * Every colour comes from the StewBeet logo: `ink` from the cast iron pot, `beet` from the
 * beetroot, `leaf` from its leaves. Contrast was measured against ink-950 (see
 * specs/002-website-redesign/research.md): ink-400 text is 6.8:1, beet-400 6.1:1, leaf-400 10.5:1,
 * and white on beet-600 is 5.7:1. ink-500 (3.4:1) is for boundaries only, never for text.
 */
const ink = {
  50: '#f8f5f0',
  100: '#eee8df',
  200: '#ddd6cc',
  300: '#c4bbb0',
  400: '#a0978c',
  500: '#6e665d',
  600: '#4b453e',
  700: '#353029',
  800: '#24211e',
  850: '#1c1a17',
  900: '#161412',
  950: '#0e0d0c',
};

const beet = {
  300: '#ff8a99',
  400: '#f25c70',
  500: '#e23a52',
  600: '#c42340',
  700: '#9e1a33',
};

const leaf = {
  400: '#7fd35b',
  500: '#5cb83a',
};

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
        ink,
        beet: { ...beet, DEFAULT: beet[400] },
        leaf: { ...leaf, DEFAULT: leaf[400] },
        mc: {
          gold: '#f2c14e',
          copper: '#d0795a',
        },
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
  plugins: [],
}
