/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        grid: {
          bg: "#f7f5f0",      // Soft warm linen background
          panel: "#f0ede6",   // Warm stone side panel
          card: "#ffffff",    // Crisp white minimalist cards
          border: "#e6e1d8",  // Delicate sand-gray lines
          text: "#2b2927",    // Deep charcoal typography
          muted: "#827a73",   // Muted clay gray
          accent: "#b57c5b",  // Soft terracotta accent
          success: "#5f7d61", // Sage green
          warning: "#c9a054", // Soft ochre yellow
          danger: "#b55b5b",  // Soft terrarosa red
          recovery: "#4a707a", // Washed slate teal
        }
      },
      fontFamily: {
        mono: ["Courier New", "Courier", "monospace"],
      }
    },
  },
  plugins: [],
}
