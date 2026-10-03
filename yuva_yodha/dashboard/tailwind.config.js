/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#3DCD58", dark: "#2BA842", soft: "#3DCD5822" },
        navy: { 950: "#07142A", 900: "#0C1E3C", 800: "#12294D", 700: "#1A3660", 600: "#244574" },
        warn: "#F59E0B",
        danger: "#EF4444",
      },
      fontFamily: { sans: ["Inter", "system-ui", "Segoe UI", "Roboto", "Arial", "sans-serif"] },
    },
  },
  plugins: [],
};
