/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border, 214.3 31.8% 91.4%))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        ocean: {
          50: '#e6f4ff',
          100: '#b3e0ff',
          200: '#80ccff',
          300: '#4db8ff',
          400: '#1aa3ff',
          500: '#0086e6',
          600: '#0069b3',
          700: '#004d80',
          800: '#00304d',
          900: '#001a2b',
        },
      },
      borderColor: {
        DEFAULT: 'hsl(var(--border, 214.3 31.8% 91.4%))',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
