import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#070a18",
          panel: "#11162a",
          cyan: "#2dfcff",
          magenta: "#ff3df2",
          violet: "#8b5cf6",
          muted: "#96a4c7",
        },
      },
      boxShadow: {
        neon: "0 0 24px rgba(45, 252, 255, 0.22)",
        magenta: "0 0 24px rgba(255, 61, 242, 0.18)",
      },
    },
  },
  plugins: [],
};

export default config;
