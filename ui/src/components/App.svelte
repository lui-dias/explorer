<script lang="ts">
	import { onMount } from 'svelte'
	import { E } from '../event'
	import {
		cwd,
		cwdSplit,
		disks,
		explorerItems,
		history,
		historyIndex,
		isExplorerFocused,
		isMultipleSelected,
		searchItems,
		selected,
		selectedQuickAccess,
		settings,
		sortType,
		sortTypeReversed,
	} from '../store'
	import type { TSortTypes } from '../types'
	import { createWs, py, setPath, sortItems, waitWsOpen, xIsWhatPercentOfY } from '../utils'
	import Arrows from './Arrows.svelte'
	import ContextMenu from './ContextMenu/ContextMenu.svelte'
	import Cwd from './Cwd.svelte'
	import Disks from './Disks.svelte'
	import Footer from './Footer.svelte'
	import Loading from './Loading.svelte'
	import New from './New.svelte'
	import Preview from './Preview.svelte'
	import QuickAccess from './QuickAccess.svelte'
	import Search from './Search.svelte'
	import Settings from './Settings.svelte'
	import Virtualist from './Virtualist.svelte'
	import WindowButtons from './WindowButtons.svelte'
	import Accordion from './ui/Accordion.svelte'
	import Icon from './ui/Icon.svelte'

	let explorerNode: HTMLDivElement
	let explorerItemsNode: HTMLUListElement
	let asideNode: HTMLElement

	let isInBorder = false
	let isMouseDown = false
	let lastX = 0

	let el = 0
	let ew = 0
	let aw = 0

	let isLoading = true

	const back = E.back
	const forward = E.forward

	onMount(async () => {
		createWs()
		await waitWsOpen()

		console.log('ready')

		const config = await py.get_config()

		settings.subscribe(async v => {
			await py.set_config(v)
		})

		settings.set(config)

		document.documentElement.style.setProperty('--primary', config.colors.primary)
		document.documentElement.style.setProperty('--accent', config.colors.accent)
		document.documentElement.style.setProperty('--text', config.colors.text)
		document.documentElement.style.setProperty('--background', config.colors.background)
		document.documentElement.style.setProperty('--divider', config.colors.divider)

		// Load data from localStorage
		sortType.set((await py.get('sortType')) || ($sortType as TSortTypes))
		sortTypeReversed.set((await py.get('sortTypeReversed')) || $sortTypeReversed)
		setPath((await py.get('cwd')) || (await py.pwd()))

		sortType.subscribe(async () => {
			const explorerSort = sortItems($explorerItems)
			const searchSort = sortItems($searchItems)

			if ($sortTypeReversed) {
				explorerSort.reverse()
				searchSort.reverse()
			}

			explorerItems.set(explorerSort)
			searchItems.set(searchSort)

			await py.set('sortType', $sortType)
		})

		sortTypeReversed.subscribe(async () => {
			const explorerSort = sortItems($explorerItems)
			const searchSort = sortItems($searchItems)

			if ($sortTypeReversed) {
				explorerSort.reverse()
				searchSort.reverse()
			}

			explorerItems.set(explorerSort)
			searchItems.set(searchSort)

			await py.set('sortTypeReversed', $sortTypeReversed)
		})

		cwd.subscribe(async v => {
			if (v) {
				searchItems.set([])
				await py.set('cwd', $cwd)
				cwdSplit.set($cwd.split('/'))
				await E.stopAllFind()

				console.time('reload')
				await E.reload()
				console.timeEnd('reload')
			}
		})

		historyIndex.subscribe(v => {
			cwd.set($history[$historyIndex])
		})

		disks.set(await py.disksInfo())

		const components = await py.get('components')

		if (components) {
			el = components.explorer.left
			ew = components.explorer.width
			aw = components.aside.width
		}

		isLoading = false
	})

	$: if (explorerNode && asideNode && el && ew && aw) {
		explorerNode.style.left = `${el}px`
		explorerNode.style.width = `${ew}%`
		asideNode.style.width = `${aw}%`
	}
</script>

<svelte:window
	on:click={e => {
		const preview = document.querySelector('._preview')
		const cwd = document.querySelector('#cwd')

		if (!preview || !cwd) return

		// @ts-ignore
		const isInCwd = e.target === cwd || cwd.contains(e.target)
		// @ts-ignore
		const isInPreview = e.target === preview || preview.contains(e.target)

		if (
			explorerNode &&
			!isInCwd &&
			!isInPreview &&
			// @ts-ignore
			(explorerNode.contains(e.target) || e.target === explorerNode)
		) {
			isExplorerFocused.set(true)
		} else {
			isExplorerFocused.set(false)
		}
	}}
	on:mousedown={e => {
		if (e.button == 3) {
			back()
		} else if (e.button == 4) {
			forward()
		}
	}}
	on:mouseup={e => {
		isMouseDown = false
	}}
	on:mousemove={async e => {
		const rect = explorerNode.getBoundingClientRect()

		const l = rect.left
		const w = rect.width

		const ww = window.innerWidth
		const x = e.clientX

		const isLeftBorder = x < l + 10

		if (isLeftBorder) {
			isInBorder = true
			document.body.style.cursor = 'col-resize'
		} else if (!isMouseDown) {
			isInBorder = false
			document.body.style.cursor = 'default'
		}

		if (isMouseDown) {
			const diffX = x - lastX

			lastX = x

			el = l + diffX
			ew = xIsWhatPercentOfY(w - diffX, ww)
			aw = xIsWhatPercentOfY(ww - (w - diffX - 14), ww)

			const components = (await py.get('components')) || {}

			components['explorer'] = { width: ew, left: el }
			components['aside'] = { width: aw }

			await py.set('components', components)
		}
	}}
	on:keyup={e => {
		if (e.key === 'Control') {
			isMultipleSelected.set(false)
		}
	}}
	on:keydown={async e => {
		if (e.key === 'Control') {
			isMultipleSelected.set(true)
		}

		if (e.ctrlKey && e.key === 'a') {
			if ($isExplorerFocused) {
				selected.set($explorerItems)
			}
		}

		if (e.ctrlKey && e.key === 'v') {
			if ($isExplorerFocused) {
				await E.paste($cwd)
				await E.reload()
			}
		}

		if ($selected.length === 0) return

		if (e.ctrlKey && e.key === 'c') {
			if ($selected.length > 1 && $isExplorerFocused) {
				const paths = $selected.map(i => i.path)
				await E.copy(paths)

				await E.footerText({
					text: `Copied ${paths.length} items to clipboard`,
					type: 'info',
				})
			}
		}

		if (e.key === 'F2') {
			if ($selected.length > 1) {
				await E.footerText({
					text: 'Cannot rename multiple items',
					type: 'warning',
				})

				return
			}

			explorerItems.set(
				$explorerItems.map(i => {
					if (!$selected) {
						return i
					}

					if (i.path === $selected[0].path) {
						return {
							...i,
							isEditMode: true,
							action: 'rename',
						}
					}

					return i
				}),
			)
		}

		if (e.key === 'Delete') {
			await E.delete(
				$selected.map(i => i.path),
				!e.shiftKey,
			)
		}
	}}
/>

<ContextMenu />
<Settings />

{#if isMouseDown}
	<span class="absolute inset-0 text-white z-10">{aw.toFixed(2)}% | {ew.toFixed(2)}%</span>
{/if}

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
	class="flex w-full h-full dark:bg-zinc-100 isolate"
	class:dark:bg-zinc-800={isLoading}
	on:click={e => {
		// Idk other way to select all items
		const allItems = document.querySelectorAll('._item')
		const preview = document.querySelector('._preview')

		for (const item of allItems) {
			// @ts-ignore
			if (item.contains(e.target)) {
				return
			}

			// @ts-ignore
			if (e.target === preview || preview?.contains(e.target)) {
				return
			}
		}

		selected.set([])
		selectedQuickAccess.set(null)
	}}
>
	{#if isLoading}
		<Loading />
	{:else}
		<aside
			bind:this={asideNode}
			class="w-[266px] p-6 px-8 pt-[30px] h-full bg-zinc-200 absolute left-0 -z-20 isolate after:w-full after:h-full after:absolute after:top-0 after:left-0 after:-z-10 after:bg-[rgba(0,0,0,0.65)]"
		>
			<div class="space-y-10">
				<Accordion class="w-full [&>*]:w-full" open>
					<div slot="trigger" class="flex justify-between items-center w-full" let:open>
						<strong class="text-[#ececec] tracking-wide font-inter">
							Quick access
						</strong>
						<Icon
							icon="OtherChevron"
							class={`${
								open ? 'rotate-[270deg]' : 'rotate-180'
							} transition-transform duration-300 fill-[#b9b9b9]`}
						/>
					</div>
					<QuickAccess slot="content" />
				</Accordion>

				<div>
					<Accordion class="w-full [&>*]:w-full">
						<div
							slot="trigger"
							class="flex justify-between items-center w-full"
							let:open
						>
							<strong
								class="text-[#ececec] dark:text-text-light tracking-wide font-inter"
							>
								Disks
							</strong>
							<Icon
								icon="OtherChevron"
								class={`${
									open ? 'rotate-[270deg]' : 'rotate-180'
								} transition-transform duration-300 fill-[#b9b9b9]`}
							/>
						</div>
						<Disks slot="content" />
					</Accordion>
				</div>
			</div>

			<div class="absolute top-0 left-0 -z-10 w-full h-full bg-[url('/bg.svg')]" />
		</aside>

		<div
			bind:this={explorerNode}
			on:mousedown={e => {
				isMouseDown = true
				lastX = e.clientX
			}}
			class="flex flex-col ml-auto w-[calc(100%-250px)] h-full bg-gradient-to-b dark:from-[#32373e] dark:to-[#16171b] rounded-l-2xl"
		>
			<WindowButtons />

			<div
				class="flex flex-col w-full h-full z-10 px-3 shadow-[-3px_0_20px_rgba(0,0,0,0.1)]"
				style="clip-path: inset(0px 0px 0px -25px);"
			>
				<div class="flex items-center my-3">
					<Cwd />
				</div>

				<div class="flex w-full h-full">
					<div class="flex flex-col w-full h-full">
						<div class="flex items-center h-20 gap-x-4" id="actions">
							<Arrows />
							<New />
							<Search />
						</div>
						<div class="flex w-full h-full">
							<div class="w-full h-full">
								<div class="flex">
									<span
										class="text-[#7f8388] text-left border-r border-[#7f8388] text-sm w-[50%]"
										>Name</span
									>
									<span
										class="text-[#7f8388] text-left border-r border-[#7f8388] pl-2 text-sm w-[20%]"
										>Modified</span
									>
									<span
										class="text-[#7f8388] text-left border-r border-[#7f8388] pl-2 text-sm w-[15%]"
										>Type</span
									>
									<span
										class="text-[#7f8388] text-left border-r border-[#7f8388] pl-2 text-sm w-[15%]"
										>Size</span
									>
								</div>
								<ul bind:this={explorerItemsNode} class="h-full">
									<Virtualist />
								</ul>
							</div>
							<Preview />
						</div>
					</div>
				</div>
			</div>
			<Footer />
		</div>
	{/if}
</div>
