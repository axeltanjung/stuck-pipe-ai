/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        dark: {
          900: "#0a0e17",
          800: "#111827",
          700: "#1a2035",
          600: "#243049",
        },
        neon: {
          blue: "#00d4ff",
          green: "#00ff88",
          orange: "#ff8800",
          red: "#ff3366",
          purple: "#a855f7",
        },
      },
      animation: {
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        glow: {
          "0%": { boxShadow: "0 0 5px rgba(0, 212, 255, 0.2)" },
          "100%": { boxShadow: "0 0 20px rgba(0, 212, 255, 0.4)" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
}
