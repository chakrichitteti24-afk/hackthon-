/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0f",
        primary: "#00ff9f",
        secondary: "#00d4ff",
        alert: "#ff006e",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        neon: "0 0 8px #00ff9f, 0 0 20px #00ff9f",
      },
    },
  },
  plugins: [],
};