const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: ['./school/**/*.{html,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
        mono: ['"Fira Mono"', ...defaultTheme.fontFamily.mono],
      },
      colors: {
        'ksp': '#818f3d',
        'ksp-semi-light': '#9aa564',
      },
      typography: {
        DEFAULT: {
          css: {
            'code::before': {
              content: '',
            },
            'code::after': {
              content: '',
            },
          },
        },
      },
    },
  },
  plugins: [
      require('@tailwindcss/typography'),
      require('@tailwindcss/forms'),
  ],
}
