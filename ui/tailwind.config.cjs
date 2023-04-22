const defaultTheme = require('tailwindcss/defaultTheme')

/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			fontFamily: {
				poppins: ['poppins', ...defaultTheme.fontFamily.sans],
			},
			colors: {
				primary: 'var(--primary)',
                text: 'var(--text)',
			},
		},
	},
	plugins: [require('tailwind-scrollbar')],
}
