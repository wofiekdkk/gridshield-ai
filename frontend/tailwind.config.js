/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        gp: {
          bg: "#f0f5fa",
          sidebar: "#ffffff",
          card: "#ffffff",
          border: "#e2eaf2",
          text: "#1e293b",
          muted: "#64748b",
          primary: "#3b82f6",
          primarySoft: "#eff6ff",
          accent: "#8b5cf6",
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          teal: "#14b8a6",
        }
      },
      boxShadow: {
        soft: "0 1px 3px 0 rgba(0,0,0,0.04), 0 1px 2px 0 rgba(0,0,0,0.03)",
        card: "0 4px 6px -1px rgba(0,0,0,0.04), 0 2px 4px -2px rgba(0,0,0,0.03)",
      }
    },
  },
  plugins: [],
}
