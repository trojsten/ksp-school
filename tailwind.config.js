const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: ['./school/**/*.{html,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [
      require('@tailwindcss/typography'),
  ],
}
