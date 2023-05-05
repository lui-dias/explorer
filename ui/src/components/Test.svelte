<script lang="ts">
	import { assert, sleep } from '../utils'

	setTimeout(async () => {
		async function TestCwd() {
			console.log('Testing CWD')

			const all = [...document.querySelectorAll('[data-test-id="cwd-item"]')]

			assert(!!all.find(e => e.textContent!.toLowerCase().trim() === 'c:'), 'CWD not found')
			assert(
				!!all.find(e => e.textContent!.toLowerCase().trim() === 'users'),
				'CWD not found',
			)
			assert(
				!!all.find(e => e.textContent!.toLowerCase().trim() === 'hiber'),
				'CWD not found',
			)
			assert(
				!!all.find(e => e.textContent!.toLowerCase().trim() === 'content'),
				'CWD not found',
			)
			assert(
				!!all.find(e => e.textContent!.toLowerCase().trim() === 'explorer'),
				'CWD not found',
			)

			const cwd = document.querySelector('[data-test-id="cwd"]') as HTMLDivElement
			let cwdInput = document.querySelector('[data-test-id="cwd-input"]') as HTMLInputElement

			assert(!!cwd, 'CWD not found')
			assert(!cwdInput, 'CWD input found')

			cwd.focus()
			await sleep(1)

			cwdInput = document.querySelector('[data-test-id="cwd-input"]')!

			assert(!!cwdInput, 'CWD input not found')
			assert(
				cwdInput.value === 'C:/Users/hiber/Content/explorer',
				'CWD input value not empty',
			)

			document.dispatchEvent(click)
			await sleep(1)

			cwdInput = document.querySelector('[data-test-id="cwd-input"]')!

			assert(!cwdInput, 'CWD input found')

			const reload = document.querySelector('[data-test-id="cwd-reload"]')!

			assert(!!reload, 'CWD reload not found')

			const explorerItem = '[data-test-id="explorer-item"]'
			const explorerItemName = '[data-test-id="file-name"]'

			const allFiles = [...document.querySelectorAll(explorerItem)].map(
				e => e.querySelector(explorerItemName)!.textContent,
			)

			reload.dispatchEvent(click)
			await sleep(1)

			const actualFiles = [...document.querySelectorAll(explorerItem)].map(
				e => e.querySelector(explorerItemName)!.textContent,
			)

			assert(
				allFiles.every(f => actualFiles.includes(f)),
				'Files are different',
			)
		}

		console.log('Initializing tests...')

		const click = new MouseEvent('click', {
			bubbles: true,
			cancelable: false,
			view: window,
		})

		try {
			await TestCwd()

			console.log(
				'✅ %cAll tests passed',
				'color: #44E13F; font-size: 16px; font-weight: bold;',
			)
		} catch (e: any) {
			console.error(e)
		}
	}, 1000)
</script>
