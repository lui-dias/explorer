<script lang="ts">
	import { cwd as Scwd, explorerItems, scrollExplorerToEnd } from '../store'
	import { py, assert, setPath, sleep } from '../utils'

	setTimeout(async () => {
		async function TestCwd() {
			const all = [...document.querySelectorAll('[data-test-id="cwd-item"]')]

			for (const path of pwd.split('/')) {
				assert(!!all.find(e => e.textContent!.trim() === path), `Should have ${path}`)
			}

			const cwd = document.querySelector('[data-test-id="cwd"]') as HTMLDivElement
			let cwdInput = document.querySelector('[data-test-id="cwd-input"]') as HTMLInputElement

			assert(!!cwd, 'Should have cwd')
			assert(!cwdInput, 'Should not have cwd input')

			cwd.focus()
			await sleep(1)

			cwdInput = document.querySelector('[data-test-id="cwd-input"]')!

			assert(!!cwdInput, 'Should have cwd input')
			assert(
				cwdInput.value === pwd + '/__tests',
				`Should cwd input value be ${pwd}/__tests, got ${cwdInput.value}`,
			)

			document.dispatchEvent(click)
			await sleep(1)

			cwdInput = document.querySelector('[data-test-id="cwd-input"]')!
			assert(!cwdInput, 'Should not have cwd input')

			const reload = document.querySelector('[data-test-id="cwd-reload"]')!
			assert(!!reload, 'Should have reload button')

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
				'Should all files be in explorer',
			)

			const itemsButtons = [...document.querySelectorAll('[data-test-id="cwd-item-button"]')]

			itemsButtons.at(-2)!.dispatchEvent(click)
			await sleep(1)

			assert($Scwd === pwd, 'Should have correct parent folder')
		}

		async function TestVirtualist() {
			setPath(pwd + '/__tests')
			await sleep(1)

			assert(
				$explorerItems.length === 1003,
				`Should have 1003 items, got ${$explorerItems.length}`,
			)

			const extraFiles = 3
			for (let i = 0; i < $explorerItems.length - extraFiles; i++) {
				// Exclude .txt and .py files
				if ($explorerItems[i].name.match(/^\d+$/)) {
					assert(
						$explorerItems.some(ii => parseInt(ii.name) === i),
						`Should have ${i}`,
					)
				}
			}

			const vl = document.querySelector('[data-test-id="vl"]')!
			assert(!!vl, 'Should have virtual list')

			$scrollExplorerToEnd()
			await sleep(1)

			const lastItem = [...vl.querySelectorAll('[data-test-id="explorer-item"]')]
				.at(-1)!
				.querySelector('[data-test-id="file-name"]')!

			assert(lastItem.textContent === '999', 'Should have the 999 item')
		}

		async function TestBackForward() {
			const back = document.querySelector(
				'[data-test-id="back"] > button',
			) as HTMLButtonElement
			const forward = document.querySelector(
				'[data-test-id="forward"] > button',
			) as HTMLButtonElement

			assert(!!back, 'Should have back button')
			assert(!!forward, 'Should have forward button')
			assert(forward.disabled, 'Should have disabled forward button')

			back.dispatchEvent(click)
			await sleep(1)

			assert(!forward.disabled, 'Should not have disabled forward button')
			assert($Scwd === pwd, `Should have correct parent folder, got ${$Scwd}`)

			forward.dispatchEvent(click)
			await sleep(1)

			assert($Scwd === pwd + '/__tests', `Should have correct parent folder, got ${$Scwd}`)
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

		async function TestNew() {
			const newFile = document.querySelector('[data-test-id="new-file"]')!
			const newFolder = document.querySelector('[data-test-id="new-folder"]')!

			assert(!!newFile, 'Should have new file')
			assert(!!newFolder, 'Should have new folder')

			let oldItemsLength = $explorerItems.length

			newFile.dispatchEvent(click)
			await sleep(1)

			document.dispatchEvent(click)
			await sleep(1)

			assert($explorerItems.length === oldItemsLength + 1, 'Should have 1 new item')
			assert(!!$explorerItems.find(i => i.name === 'file'), 'Should have a new file')

			oldItemsLength = $explorerItems.length

			newFolder.dispatchEvent(click)
			await sleep(1)

			document.dispatchEvent(click)
			await sleep(1)

			assert($explorerItems.length === oldItemsLength + 1, 'Should have 1 new item')
			assert(!!$explorerItems.find(i => i.name === 'folder'), 'Should have a new folder')

			document.dispatchEvent(click)
		}

		async function TestContextMenu() {
			const contextmenu = document.querySelector('[data-test-id="contextmenu"]')!

			assert(!!contextmenu, 'Should have context menu')
			assert(contextmenu.classList.contains('invisible'), 'Should be invisible')

			window.dispatchEvent(evContextmenu)
			await sleep(1)

			assert(!contextmenu.classList.contains('invisible'), 'Should be visible')
		}

		await py.setupTests()
		const pwd = await py.pwd()

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

		const evContextmenu = new MouseEvent('contextmenu')

		const hover = new MouseEvent('mouseover', {
			bubbles: true,
			cancelable: true,
			view: window,
		})

		try {
			console.log('Testing CWD')
			await TestCwd()

			console.log('Testing Virtualist')
			await TestVirtualist()

			console.log('Testing Back/Forward')
			await TestBackForward()

			console.log('Testing Search')
			await TestSearch()

			console.log('Testing New')
			await TestNew()

			console.log('Testing Context Menu')
			await TestContextMenu()

			console.log(
				'✅ %cAll tests passed',
				'color: #44E13F; font-size: 16px; font-weight: bold;',
			)
		} catch (e: any) {
			console.error(e)
		}

		setPath(pwd)
		await py.clearTests()
	}, 1000)
</script>
