/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "on-tertiary-fixed-variant": "#7b2f00",
        "outline": "#867366",
        "on-secondary": "#ffffff",
        "inverse-on-surface": "#f3f0ea",
        "inverse-primary": "#ffb783",
        "on-primary-container": "#693300",
        "surface-container": "#f0eee7",
        "surface-tint": "#944a00",
        "on-surface-variant": "#544438",
        "on-primary": "#ffffff",
        "surface-variant": "#e5e2db",
        "primary-fixed-dim": "#ffb783",
        "secondary-container": "#ffd97d",
        "background": "#fcf9f2",
        "surface-container-highest": "#e5e2db",
        "on-background": "#1c1c18",
        "on-secondary-fixed": "#251a00",
        "on-secondary-container": "#785d09",
        "error": "#ba1a1a",
        "surface-bright": "#fcf9f2",
        "on-error": "#ffffff",
        "surface-dim": "#dcdad3",
        "on-secondary-fixed-variant": "#594400",
        "primary-fixed": "#ffdcc5",
        "on-tertiary-container": "#722b00",
        "surface-container-lowest": "#ffffff",
        "on-primary-fixed-variant": "#713700",
        "on-primary-fixed": "#301400",
        "secondary-fixed-dim": "#e7c269",
        "on-tertiary": "#ffffff",
        "surface": "#fcf9f2",
        "tertiary": "#a14000",
        "tertiary-fixed": "#ffdbcc",
        "tertiary-fixed-dim": "#ffb694",
        "tertiary-container": "#ff915a",
        "surface-container-low": "#f6f3ec",
        "primary": "#944a00",
        "on-surface": "#1c1c18",
        "inverse-surface": "#31312c",
        "error-container": "#ffdad6",
        "secondary": "#765b06",
        "primary-container": "#ff9238",
        "secondary-fixed": "#ffdf96",
        "on-tertiary-fixed": "#351000",
        "outline-variant": "#d9c2b3",
        "surface-container-high": "#ebe8e1",
        "on-error-container": "#93000a",
        // Цвета со страницы Login
        "primary-light": "#ff9238",
        "primary-dark": "#6b3500",
      },
      fontFamily: {
        "headline": ["Manrope", "sans-serif"],
        "body": ["Inter", "sans-serif"],
        "label": ["Inter", "sans-serif"]
      },
      // Анимации со страницы Login
      animation: {
        'blob': 'blob 10s infinite',
        'float-fast': 'float 6s ease-in-out infinite',
        'float-slow': 'float 12s ease-in-out infinite',
        'float-reverse': 'float 9s ease-in-out infinite reverse',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        blob: {
          '0%, 100%': { transform: 'translate(0px, 0px) scale(1)', opacity: 0.4 },
          '33%': { transform: 'translate(50px, -70px) scale(1.2)', opacity: 0.6 },
          '66%': { transform: 'translate(-30px, 30px) scale(0.9)', opacity: 0.4 },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '50%': { transform: 'translateY(-30px) rotate(3deg)' },
        }
      }
    },
  },
  plugins: [],
}