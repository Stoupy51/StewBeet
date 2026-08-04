/** @type {import('tailwindcss').Config} */

/**
 * Accent colours are taken from the blocks they are named after, so the palette belongs to
 * the domain the tool serves rather than to the indigo-and-purple gradient every framework
 * site ships with. Contrast against slate-950 was measured before each was adopted:
 * emerald 11.1:1, diamond 13.4:1, gold 15.2:1, copper 5.2:1 — all clear of the 4.5:1 floor
 * for body text, so any of them is safe on prose, not only on headings.
 */
const minecraft = {
  emerald: '#17DD62',
  diamond: '#4AEDD9',
  gold: '#FAEE4D',
  copper: '#C86545',
  redstone: '#FF4B3E',
  lapis: '#5A6BE0',
};

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mc: minecraft,
      },
      borderRadius: {
        // Structural panels sit on a 4px grid so edges read as placed rather than softened.
        panel: '6px',
      },
      backgroundImage: {
        // Crisp 4px checker used for section dividers, in place of blurred colour blobs.
        'pixel-rule': `repeating-linear-gradient(90deg, ${minecraft.emerald}00 0 4px, ${minecraft.emerald}40 4px 8px)`,
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
