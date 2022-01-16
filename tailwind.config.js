const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: ['./school/**/*.{html,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
        mono: ['"Fira Mono"', ...defaultTheme.fontFamily.mono],
      },
    },
  },
  plugins: [
      require('@tailwindcss/typography'),
  ],
}
