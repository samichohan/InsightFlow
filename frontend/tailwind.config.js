/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: { base: "#080b14", card: "#0f1729", raised: "#141d33" },
        border: { subtle: "#1e293b", glow: "#2d3f5e" },
        accent: { blue: "#38bdf8", violet: "#818cf8", green: "#34d399", amber: "#fbbf24", pink: "#f472b6" }
      },
      fontFamily: {
        display: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      },
      animation: {
        "fade-up": "fadeUp 0.4s ease-out forwards",
        "pulse-ring": "pulseRing 1.8s ease-out infinite",
        "shimmer": "shimmer 1.5s infinite"
      },
      keyframes: {
        fadeUp: { "0%": { opacity: 0, transform: "translateY(12px)" }, "100%": { opacity: 1, transform: "translateY(0)" } },
        pulseRing: { "0%": { boxShadow: "0 0 0 0 rgba(56,189,248,0.4)" }, "70%": { boxShadow: "0 0 0 10px rgba(56,189,248,0)" }, "100%": { boxShadow: "0 0 0 0 rgba(56,189,248,0)" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } }
      }
    }
  },
  plugins: []
}
