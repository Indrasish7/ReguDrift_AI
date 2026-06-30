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
        background: "#0B0F19",
        surface: "#131314",
        "surface-dim": "#131314",
        "surface-bright": "#3a393a",
        "surface-container-lowest": "#0e0e0f",
        "surface-container-low": "#1c1b1c",
        "surface-container": "#201f20",
        "surface-container-high": "#2a2a2b",
        "surface-container-highest": "#353435",
        "on-surface": "#e5e2e2",
        "on-surface-variant": "#c6c6cc",
        "inverse-surface": "#e5e2e2",
        "inverse-on-surface": "#313031",
        outline: "#909096",
        "outline-variant": "#46464c",
        primary: "#c3c6d4",
        "on-primary": "#2c303b",
        "primary-container": "#0b0f19",
        "on-primary-container": "#787b88",
        "inverse-primary": "#5a5e6a",
        secondary: "#bcc7de",
        "on-secondary": "#263143",
        "secondary-container": "#3e495d",
        "on-secondary-container": "#aeb9d0",
        tertiary: "#dbc2b1",
        "on-tertiary": "#3d2d22",
        "tertiary-container": "#180c04",
        "on-tertiary-container": "#8d7869",
        error: "#ffb4ab",
        "on-error": "#690005",
        "error-container": "#93000a",
        "on-error-container": "#ffdad6",
      },
      borderRadius: {
        DEFAULT: "0.125rem", // 2px
        lg: "0.25rem", // 4px
        xl: "0.5rem", // 8px
        full: "0.75rem", // 12px
      },
      spacing: {
        "density-high": "4px",
        unit: "4px",
        "component-gap": "8px",
        "container-padding": "24px",
        "density-medium": "12px",
        gutter: "16px",
      },
      fontFamily: {
        "display-lg": ["var(--font-hanken-grotesk)", "sans-serif"],
        "headline-md": ["var(--font-hanken-grotesk)", "sans-serif"],
        "title-sm": ["var(--font-inter)", "sans-serif"],
        "body-md": ["var(--font-inter)", "sans-serif"],
        "body-sm": ["var(--font-inter)", "sans-serif"],
        "code-terminal": ["var(--font-jetbrains-mono)", "monospace"],
        "label-caps": ["var(--font-jetbrains-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
