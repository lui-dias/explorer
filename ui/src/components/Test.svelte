<script lang="ts">
	import { __pywebview, assert, setPath, sleep } from '../utils'
	import { explorerItems, scrollExplorerToEnd, cwd as Scwd } from '../store'

	setTimeout(async () => {
		async function TestCwd() {
			const all = [...document.querySelectorAll('[data-test-id="cwd-item"]')]

			for (const path of pwd.split('/')) {
				assert(!!all.find(e => e.textContent!.trim() === path), `CWD ${path} not found`)
			}

			const cwd = document.querySelector('[data-test-id="cwd"]') as HTMLDivElement
			let cwdInput = document.querySelector('[data-test-id="cwd-input"]') as HTMLInputElement

			assert(!!cwd, 'CWD not found')
			assert(!cwdInput, 'CWD input found')

			cwd.focus()
			await sleep(1)

			cwdInput = document.querySelector('[data-test-id="cwd-input"]')!

			assert(!!cwdInput, 'CWD input not found')
			assert(cwdInput.value === pwd + '/seed', 'CWD input value not empty')

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

			const itemsButtons = [...document.querySelectorAll('[data-test-id="cwd-item-button"]')]

			itemsButtons.at(-2)!.dispatchEvent(click)
			await sleep(1)

			assert($Scwd === pwd, 'Parent folder not found')
		}

		async function TestVirtualist() {
			setPath(pwd + '/seed')
			await sleep(1)

			assert($explorerItems.length === 1000, 'Incorrect items length')

			for (let i = 0; i < $explorerItems.length; i++) {
				assert(parseInt($explorerItems[i].name) === i, `Missing item in explorer: ${i}`)
			}

			const vl = document.querySelector('[data-test-id="vl"]')!
			assert(!!vl, 'Virtual list not found')

			$scrollExplorerToEnd()
			await sleep(1)

			const lastItem = [...vl.querySelectorAll('[data-test-id="explorer-item"]')]
				.at(-1)!
				.querySelector('[data-test-id="file-name"]')!

			assert(lastItem.textContent === '999', 'Last item not found')
		}

		console.log('Initializing tests...')

		const user = await __pywebview.user()
		const pwd = await __pywebview.pwd()

		setPath(pwd + '/seed')
		await sleep(1)

		const click = new MouseEvent('click', {
			bubbles: true,
			cancelable: false,
			view: window,
		})

		try {
			console.log('Testing CWD')
			await TestCwd()

			console.log('Testing Virtualist')
			await TestVirtualist()

			console.log(
				'✅ %cAll tests passed',
				'color: #44E13F; font-size: 16px; font-weight: bold;',
			)
		} catch (e: any) {
			console.error(e)
		}
	}, 1000)
</script>
