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
		isLoading,
		isMultipleSelected,
		searchItems,
		selected,
		selectedQuickAccess,
		settings,
		sortType,
		sortTypeReversed,
		installedApps,
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

	let explorerLeft = 0
	let explorerWidth = 0
	let asideWidth = 0

	let quickAccessOpen = true
	let disksOpen = false

	const back = E.back
	const forward = E.forward

	onMount(async () => {
		createWs()
		await waitWsOpen()

		console.log('ready')

		const config = await py.getConfig()

		settings.subscribe(async v => {
			await py.setConfig(v)
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

		// Sort items
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
		// ----------

		// Reload explorer items when cwd changes
		cwd.subscribe(async v => {
			if (v) {
				searchItems.set([])
				await py.set('cwd', $cwd)
				cwdSplit.set($cwd.split('/'))
				await py.deleteAllStreamsFind()
				await E.reload()
			}
		})

		// Update history when index changes
		historyIndex.subscribe(v => {
			cwd.set($history[$historyIndex])
		})

		// Update disks
		disks.set(await py.disksInfo())

		// Set components sizes and positions
		const components = await py.get('components')
		const accordions = await py.get('accordions')

		if (components) {
			explorerLeft = components.explorer.left
			explorerWidth = components.explorer.width
			asideWidth = components.aside.width
		}

		if (accordions) {
			quickAccessOpen = accordions.quickAccess
			disksOpen = accordions.disks
		}
		// --------

		// Update installed apps
		installedApps.set(await py.getInstalledApps())

		// Remove loading indicator
		isLoading.set(false)
	})

	// Update components positions and sizes
	// explorerLeft, explorerWidth, asideWidth can't be 0 otherwise the layout will break
	$: if (explorerNode && asideNode && explorerLeft && explorerWidth && asideWidth) {
		explorerNode.style.left = `${explorerLeft}px`
		explorerNode.style.width = `${explorerWidth}%`
		asideNode.style.width = `${asideWidth}%`
	}

	// Save accordions state
	$: if (!$isLoading) {
		async function _() {
			let accordions = (await py.get('accordions')) ?? {}

			accordions = {
				...accordions,
				...{
					quickAccess: quickAccessOpen,
					disks: disksOpen,
				},
			}

			await py.set('accordions', accordions)
		}

		_()
	}
</script>

<svelte:window
	on:click={e => {
		// Handle if explorer is focused

		const preview = document.querySelector('.preview')
		const cwd = document.querySelector('#cwd')

		if (!preview || !cwd) return

		// @ts-ignore
		const clickedInCwd = e.target === cwd || cwd.contains(e.target)
		// @ts-ignore
		const clickedInPreview = e.target === preview || preview.contains(e.target)
		// @ts-ignore
		const clickedInExplorer = explorerNode.contains(e.target) || e.target === explorerNode

		isExplorerFocused.set(
			explorerNode && !clickedInCwd && !clickedInPreview && clickedInExplorer,
		)
	}}
	on:mousedown={e => {
		// Handle custom mouse buttons

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
		// Resize aside bar

		if (!explorerNode) return

		const { left, width } = explorerNode.getBoundingClientRect()

		const ww = window.innerWidth
		const x = e.clientX

		// size of the width that the person can move the mouse in which will be considered a resize area
		const borderResizeArea = 10
		const isInLeftBorder = x < left + borderResizeArea

		isInBorder = isInLeftBorder

		if (isInLeftBorder) {
			document.body.style.cursor = 'col-resize'
		} else if (!isMouseDown) {
			document.body.style.cursor = 'default'
		}

		if (isMouseDown) {
			const diffX = x - lastX

			lastX = x

			explorerLeft = left + diffX
			explorerWidth = xIsWhatPercentOfY(width - diffX, ww)
			asideWidth = xIsWhatPercentOfY(ww - (width - diffX - 14), ww)

			// Update components in local storage
			const components = (await py.get('components')) ?? {}

			components['explorer'] = { width: explorerWidth, left: explorerLeft }
			components['aside'] = { width: asideWidth }

			await py.set('components', components)
		}
	}}
	on:keyup={e => {
		// Disable multiple selection
		if (e.key === 'Control') {
			isMultipleSelected.set(false)
		}
	}}
	on:keydown={async e => {
        // Unselect all items
		if (e.key === 'Escape') {
			selected.set([])
		}

		// Enable multiple selection
		if (e.key === 'Control') {
			isMultipleSelected.set(true)
		}

		// Select all items
		if (e.ctrlKey && e.key === 'a') {
			if ($isExplorerFocused) {
				selected.set($explorerItems)
			}
		}

		// If have any file in clipboard, it will copy to cwd
		if (e.ctrlKey && e.key === 'v') {
			if ($isExplorerFocused) {
				await py.paste($cwd)
				await E.reload()
			}
		}

		// Down requires a item to be selected
		if ($selected.length === 0) return

		// Copy all selected items to clipboard
		if (e.ctrlKey && e.key === 'c') {
			if ($selected.length > 1 && $isExplorerFocused) {
				const paths = $selected.map(i => i.path)
				await py.copy(paths.join(' '))

				await E.footerText({
					text: `Copied ${paths.length} items to clipboard`,
					type: 'info',
				})
			}
		}

		// Rename selected item to clipboard
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

		// Delete selected items
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
	<span class="absolute inset-0 text-white z-10"
		>{asideWidth.toFixed(2)}% | {explorerWidth.toFixed(2)}%</span
	>
{/if}

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
	class="flex w-full h-full dark:bg-zinc-100 isolate"
	class:dark:bg-zinc-800={$isLoading}
	on:click={e => {
		const allItems = document.querySelectorAll('.item')
		const preview = document.querySelector('.preview')

		// if click was on explorer, but not on items or preview
		for (const item of allItems) {
			// @ts-ignore
			const clickWasInItem = item.contains(e.target)
			// @ts-ignore
			const clickWasInPreview = e.target === preview || preview?.contains(e.target)

			if (clickWasInItem || clickWasInPreview) {
				return
			}
		}

		selected.set([])
		selectedQuickAccess.set(null)
	}}
>
	{#if $isLoading}
		<Loading />
	{:else}
		<aside
			bind:this={asideNode}
			class="w-[266px] p-6 px-8 pt-[30px] h-full bg-zinc-200 absolute left-0 -z-20 isolate after:w-full after:h-full after:absolute after:top-0 after:left-0 after:-z-10 after:bg-[rgba(0,0,0,0.65)]"
		>
			<div class="space-y-10">
				<Accordion class="w-full [&>*]:w-full" bind:open={quickAccessOpen}>
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
					<Accordion class="w-full [&>*]:w-full" bind:open={disksOpen}>
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
				if (isInBorder) {
					isMouseDown = true
					lastX = e.clientX
				}
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
