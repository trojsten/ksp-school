import tippy from 'tippy.js'
import 'tippy.js/dist/tippy.css'

import Alpine from 'alpinejs'
window.Alpine = Alpine
Alpine.start()

import feather from 'feather-icons'
import 'iconify-icon'
import htmx from 'htmx.org'
window.htmx = htmx

const onLoad = () => {
    tippy('[data-tippy-content]')
    feather.replace()

    window.renderMathInElement(document.body, {
      delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$', right: '$', display: false},
          {left: '\\(', right: '\\)', display: false},
          {left: '\\[', right: '\\]', display: true}
      ]
    })
}

document.addEventListener("DOMContentLoaded", () => {
    onLoad()
    htmx.onLoad(onLoad)
})
