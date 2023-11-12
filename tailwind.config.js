/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')
module.exports = {
  darkMode: 'class',
  content:  [
      './templates/**/*.{html,js}',
      './static/Typescript/*.{ts, js}'
  ],
  theme: {
    colors: {
      'purple__c': '#480773',
      'light_purple__c': '#730DD9',
      'pink__c': '#F25CCA',
      'light_pink__c': '#f9aee5',
      'green__c': '#74BF04',
      'aqua__c': '#0597F2',
      'light_aqua__c': '#82cbf9',
      colors,
    },
    extend: {},
  },
  plugins: [
    require("tailwindcss-animation-delay"),
  ],
}

