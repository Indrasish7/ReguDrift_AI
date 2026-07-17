import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#030712", // Midnight Deep Space
        surface: "#090F1C",    // Obsidian graphite glass
        "surface-dim": "#050811",
        "surface-bright": "#121B2E",
        "surface-container-lowest": "#030712",
        "surface-container-low": "#060913",
        "surface-container": "#090F1C",
        "surface-container-high": "#1E293B", // Glowing slate grey border/fill
        "surface-container-highest": "#2D3D5A",
        "on-surface": "#F8FAFC",            // Pure off-white
        "on-surface-variant": "#94A3B8",    // Muted slate grey
        "inverse-surface": "#F8FAFC",
        "inverse-on-surface": "#030712",
        outline: "#334155",
        "outline-variant": "#1E293B",       // Slate border lines
        primary: "#00F0FF",                 // Cyber Cyan
        "on-primary": "#030712",
        "primary-container": "#030712",
        "on-primary-container": "#00F0FF",
        "inverse-primary": "#00C3D9",
        secondary: "#8B5CF6",               // Cyber Purple / Glowing Violet
        "on-secondary": "#FFFFFF",
        "secondary-container": "#2E1065",
        "on-secondary-container": "#DDD6FE",
        success: "#10B981",                 // Emerald Green
        "on-success": "#FFFFFF",
        warning: "#FBBC05",
        "on-warning": "#202124",
        error: "#F43F5E",                   // Hot Magenta / Pink for drifts
        "on-error": "#FFFFFF",
      },
      borderRadius: {
        DEFAULT: "0.75rem",  // 12px modular Bento corners
        lg: "0.75rem",
        xl: "1rem",          // 16px soft corners
        "2xl": "1.5rem",     // 24px rounded widgets
        full: "9999px",
      },
      spacing: {
        "density-high": "6px",
        unit: "8px",
        "component-gap": "12px",
        "container-padding": "24px",
        "density-medium": "16px",
        gutter: "24px",
      },
      fontFamily: {
        "display-lg": ["var(--font-inter)", "sans-serif"],
        "headline-md": ["var(--font-inter)", "sans-serif"],
        "title-sm": ["var(--font-inter)", "sans-serif"],
        "body-md": ["var(--font-inter)", "sans-serif"],
        "body-sm": ["var(--font-inter)", "sans-serif"],
        "code-terminal": ["var(--font-jetbrains-mono)", "monospace"],
        "label-caps": ["var(--font-inter)", "sans-serif"],
      },
      boxShadow: {
        sm: "0 0 10px rgba(0,240,255,0.05)",
        md: "0 0 20px rgba(139,92,246,0.1)",
        lg: "0 0 30px rgba(0,240,255,0.15)",
        inset: "inset 0 0 12px rgba(30,41,59,0.3)"
      }
    },
  },
  plugins: [],
};

export default config;
