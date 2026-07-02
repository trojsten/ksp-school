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
        'ksp-dark': '#41481f',
        'ksp-semi-dark': '#565f29',
        'ksp-light': '#abb47e',
        'ksp-semi-light': '#9aa564',
      },
      typography: {
        DEFAULT: {
          css: {
            'a': {
              color: '#818f3d',
            },
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
