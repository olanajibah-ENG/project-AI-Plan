import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: "#faf5ed",
          50: "#fdfbf7",
          100: "#faf5ed",
          200: "#f0e8da",
          300: "#e3d5be",
          400: "#a89880",
          500: "#8b7a62",
          600: "#7a6652",
          700: "#5c4a38",
          800: "#3d2e1e",
          900: "#2c1810",
        },
        terracotta: {
          DEFAULT: "#c96442",
          50: "#fef4f0",
          100: "#f4d5c6",
          200: "#e8a88a",
          300: "#d98464",
          400: "#c96442",
          500: "#b05535",
          600: "#8f4229",
          700: "#6e3320",
        },
        teal: {
          DEFAULT: "#1a6b5a",
          50: "#f0faf7",
          100: "#d4ede6",
          200: "#a8dbcd",
          300: "#6ebfa8",
          400: "#3d9c84",
          500: "#1a6b5a",
          600: "#155a4b",
          700: "#10483c",
        },
        gold: {
          DEFAULT: "#b8860b",
          50: "#fdf8ec",
          100: "#f5e6c4",
          200: "#eacc86",
          300: "#d4ab3e",
          400: "#b8860b",
          500: "#9a7009",
        },
      },
      fontFamily: {
        display: ["'Reem Kufi'", "sans-serif"],
        body: ["'Readex Pro'", "sans-serif"],
      },
      boxShadow: {
        subtle: "0 1px 3px rgba(44, 24, 16, 0.06)",
        card: "0 4px 24px rgba(44, 24, 16, 0.07)",
        elevated: "0 12px 40px rgba(44, 24, 16, 0.1)",
        glow: "0 0 40px rgba(201, 100, 66, 0.12)",
        "inner-glow": "inset 0 1px 2px rgba(44, 24, 16, 0.06)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-in-right": {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        "slide-in-left": {
          "0%": { opacity: "0", transform: "translateX(-20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        "typing-dot": {
          "0%, 60%, 100%": { opacity: "0.3", transform: "scale(0.8)" },
          "30%": { opacity: "1", transform: "scale(1)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-6px)" },
        },
      },
      animation: {
        "fade-up": "fade-up 500ms ease-out both",
        "fade-in": "fade-in 400ms ease-out both",
        "slide-in-right": "slide-in-right 400ms ease-out both",
        "slide-in-left": "slide-in-left 400ms ease-out both",
        "typing-dot": "typing-dot 1.4s infinite",
        float: "float 3s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-rtl")],
};

export default config;
