/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#F5F7FA",
        sidebar: "#FFFFFF",
        card: "#FFFFFF",
        border: "#E5E7EB",
        primary: "#2563EB",
        secondary: "#14B8A6",
        success: "#10B981",
        warning: "#F59E0B",
        error: "#EF4444",
        text: "#111827",
        muted: "#6B7280",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Helvetica Neue", "Arial"],
      },
      boxShadow: {
        soft: "0 8px 24px rgba(16,24,40,0.06)",
      },
    },
  },
  plugins: [],
};