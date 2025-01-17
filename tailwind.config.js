/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  theme: {
    extend: {
      colors: {
        primary: "#040D12",
        secondary: "#183D3D",
        tertiary: "#355C7D",
        accent: {
          dark: "#5C8374",
          light: "#93B1A6",
        },
      },
      fontFamily: {
        inter: ["Inter", "serif"],
        montserrat: ["Montserrat", "serif"],
      },
      width: {
        96: "24rem",
      },
    },
  },
  plugins: [],
};
