/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark theme colors
        'dark': {
          'bg': '#0f0f0f',
          'panel': '#1a1a1a',
          'panel-alt': '#242424',
          'border': '#2a2a2a',
          'text': '#e5e5e5',
          'text-muted': '#a0a0a0',
        },
        // Light theme colors
        'light': {
          'bg': '#fafafa',
          'panel': '#f5f5f0',
          'panel-alt': '#f0f0e8',
          'border': '#e0e0e0',
          'text': '#1a1a1a',
          'text-muted': '#666666',
        },
        // Accent colors
        'accent': {
          'blue': '#3b82f6',
          'cyan': '#06b6d4',
          'emerald': '#10b981',
          'orange': '#f59e0b',
        }
      },
      borderRadius: {
        'custom': '40px',
        'custom-sm': '18px',
      }
    },
  },
  plugins: [],
}