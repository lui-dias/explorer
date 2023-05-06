<script lang="ts">
	import { __pywebview, assert, setPath, sleep } from '../utils'
	import { explorerItems, scrollExplorerToEnd, cwd as Scwd, history } from '../store'

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
			assert(cwdInput.value === pwd + '/__tests', 'CWD input value not empty')

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
			setPath(pwd + '/__tests')
			await sleep(1)

			assert($explorerItems.length === 1003, 'Incorrect items length')

			const extraFiles = 3
			for (let i = 0; i < $explorerItems.length - extraFiles; i++) {
				// Exclude .txt and .py files
				if ($explorerItems[i].name.match(/^\d+$/)) {
					assert(
						$explorerItems.some(ii => parseInt(ii.name) === i),
						`Missing item in explorer: ${i}`,
					)
				}
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

		async function TestBackForward() {
			const back = document.querySelector(
				'[data-test-id="back"] > button',
			) as HTMLButtonElement
			const forward = document.querySelector(
				'[data-test-id="forward"] > button',
			) as HTMLButtonElement

			assert(!!back, 'Back button not found')
			assert(!!forward, 'Forward button not found')
			assert(forward.disabled, 'Back button disabled')

			back.dispatchEvent(click)
			await sleep(1)

			assert(!forward.disabled, 'Forward button enabled')
			assert($Scwd === pwd, 'Parent folder not found')

			forward.dispatchEvent(click)
			await sleep(1)

			assert($Scwd === pwd + '/__tests', 'Parent folder not found')
		}

		async function TestSearch() {
			const searchIcon = document.querySelector('[data-test-id="search-icon"]')!
			assert(!!searchIcon, 'Should have search icon')

			searchIcon.dispatchEvent(click)
			await sleep(1.5)

			assert(
				!document.querySelector('[data-test-id="search-icon"]'),
				'Should not have search icon',
			)

			const searchInput = document.querySelector(
				'[data-test-id="search"] > input',
			) as HTMLInputElement
			assert(!!searchInput, 'Should have search input')

			searchInput.value = 'test.txt'
			searchInput.dispatchEvent(evInput)
			searchInput.dispatchEvent(evEnter)
			await sleep(1)

			let explorerItems = [...document.querySelectorAll('[data-test-id="explorer-item"]')]
			let itemName = explorerItems
				.at(-1)!
				.querySelector('[data-test-id="file-name"]')!.textContent

			assert(explorerItems.length === 1, 'Should have 1 item')
			assert(itemName === 'test.txt', 'Should have the right item')

			searchInput.value = '/py$/'
			searchInput.dispatchEvent(evInput)
			searchInput.dispatchEvent(evEnter)
			await sleep(1)

			explorerItems = [...document.querySelectorAll('[data-test-id="explorer-item"]')]

			let itemsName = explorerItems.map(
				e => e.querySelector('[data-test-id="file-name"]')!.textContent,
			)

			assert(explorerItems.length === 2, 'Should have 1 item')
			assert(
				itemsName.includes('foo.py') && itemsName.includes('bar.py'),
				'Should have the right item',
			)

			searchInput.value = '*.py'
			searchInput.dispatchEvent(evInput)
			searchInput.dispatchEvent(evEnter)
			await sleep(1)

			explorerItems = [...document.querySelectorAll('[data-test-id="explorer-item"]')]
			itemsName = explorerItems.map(
				e => e.querySelector('[data-test-id="file-name"]')!.textContent,
			)

			assert(explorerItems.length === 2, 'Should have 2 item')
			assert(
				itemsName.includes('foo.py') && itemsName.includes('bar.py'),
				'Should have the right item',
			)
		}

		await __pywebview.setupTests()
		const pwd = await __pywebview.pwd()

		setPath(pwd + '/__tests')
		await sleep(1)

		const click = new MouseEvent('click', {
			bubbles: true,
			cancelable: false,
			view: window,
		})

		const evEnter = new KeyboardEvent('keydown', {
			key: 'Enter',
		})
		const evInput = new KeyboardEvent('input', { bubbles: true })

		try {
			console.log('Testing CWD')
			await TestCwd()

			console.log('Testing Virtualist')
			await TestVirtualist()

			console.log('Testing Back/Forward')
			await TestBackForward()

			console.log('Testing Search')
			await TestSearch()

			console.log(
				'✅ %cAll tests passed',
				'color: #44E13F; font-size: 16px; font-weight: bold;',
			)
		} catch (e: any) {
			console.error(e)
		}

		setPath(pwd)
		await __pywebview.clearTests()
	}, 1000)
</script>
