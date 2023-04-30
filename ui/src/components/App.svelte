<script lang="ts">
	import { onMount } from 'svelte'
	import { events } from '../event'
	import {
		cwd,
		cwdSplit,
		explorerItems,
		history,
		historyIndex,
		isMultipleSelected,
		searchItems,
		selected,
		selectedQuickAccess,
		settings,
		sortType,
	} from '../store'
	import type { TSortTypes } from '../types'
	import { __pywebview, sortItems } from '../utils'
	import Arrows from './Arrows.svelte'
	import Cwd from './CWD.svelte'
	import ContextMenu from './ContextMenu/ContextMenu.svelte'
	import Footer from './Footer.svelte'
	import Loading from './Loading.svelte'
	import QuickAccess from './QuickAccess.svelte'
	import Search from './Search.svelte'
	import Settings from './Settings.svelte'
	import Virtualist from './Virtualist.svelte'
	import WindowButtons from './WindowButtons.svelte'

	let explorerItemsNode: HTMLUListElement

	let isLoading = true

	const back = () => events.emit('back')
	const forward = () => events.emit('forward')

	onMount(async () => {
		// Wait pywebview to be ready
		await __pywebview.__wait()
		console.log('ready')

		const config = await __pywebview.get_config()

		settings.subscribe(async v => {
			await __pywebview.set_config(v)
		})

		settings.set(config)

		document.documentElement.style.setProperty('--primary', config.colors.primary)
		document.documentElement.style.setProperty('--accent', config.colors.accent)
		document.documentElement.style.setProperty('--text', config.colors.text)
		document.documentElement.style.setProperty('--background', config.colors.background)
		document.documentElement.style.setProperty('--divider', config.colors.divider)

		// Load data from localStorage
		sortType.set((localStorage.getItem('sortType') || $sortType) as TSortTypes)
		cwd.set(localStorage.getItem('cwd') || (await __pywebview.home()))

		cwdSplit.set($cwd.split('/'))

		// Add each parent path to history
		// Example: /home/user/Downloads
		// history: ['/home', '/home/user', '/home/user/Downloads']
		const h = [] as string[]
		for (let i = 0; i < $cwdSplit.length; i++) {
			h.push($cwdSplit.slice(0, i + 1).join('/'))
		}
		history.set(h)
		historyIndex.set(h.length - 1)

		sortType.subscribe(() => {
			explorerItems.set(sortItems($explorerItems))
			searchItems.set(sortItems($searchItems))

			localStorage.setItem('sortType', $sortType)
		})

		cwd.subscribe(v => {
			if (v) {
				localStorage.setItem('cwd', $cwd)
				events.emit('stop_all_find')
				events.emit('reload')
			}
		})

		historyIndex.subscribe(v => {
			cwd.set($history[$historyIndex])
		})

		isLoading = false
	})
</script>

<svelte:window
	on:mousedown={e => {
		if (e.button == 3) {
			back()
		} else if (e.button == 4) {
			forward()
		}
	}}
	on:keyup={e => {
		if (e.key === 'Control') {
			isMultipleSelected.set(false)
		}
	}}
	on:keydown={e => {
		if (e.key === 'Control') {
			isMultipleSelected.set(true)
		}

		if (e.ctrlKey && e.key === 'a') {
			selected.set($explorerItems)
		}

		if ($selected.length === 0) return

		if (e.key === 'F2') {
			if ($selected.length > 1) {
				events.emit('footer_text', {
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
			events.emit(
				'delete',
				$selected.map(i => i.path),
				!e.shiftKey,
			)
		}
	}}
/>

<ContextMenu />
<Settings />

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
	class="w-full h-full dark:bg-zinc-100 flex overflow-y-hidden isolate"
	class:dark:bg-zinc-800={isLoading}
	on:click={e => {
		// Idk other way to select all items
		const allItems = document.querySelectorAll('._item')

		for (const item of allItems) {
			// @ts-ignore
			if (item.contains(e.target)) {
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
			class="w-[266px] p-6 px-8 pt-[30px] h-full bg-zinc-200 absolute left-0 -z-20 isolate after:w-full after:h-full after:absolute after:top-0 after:left-0 after:-z-10 after:bg-[rgba(0,0,0,0.65)]"
		>
			<strong class="text-lg text-[#ececec] dark:text-text-light tracking-wide font-inter">
				Quick access
			</strong>
			<QuickAccess />

			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="100%"
				height="100%"
				class="absolute left-0 top-0 -z-10"
				><defs
					><linearGradient
						gradientTransform="rotate(70 .5 .5)"
						x1="50%"
						y1="0%"
						x2="50%"
						y2="100%"
						id="a"
						><stop stop-color="hsl(195, 75%, 43%)" offset="0%" /><stop
							stop-color="hsl(235, 84%, 55%)"
							offset="100%"
						/></linearGradient
					><filter
						id="b"
						x="-20%"
						y="-20%"
						width="140%"
						height="140%"
						filterUnits="objectBoundingBox"
						primitiveUnits="userSpaceOnUse"
						color-interpolation-filters="sRGB"
						><feTurbulence
							type="fractalNoise"
							baseFrequency="0.005 0.003"
							numOctaves="2"
							seed="2"
							stitchTiles="stitch"
							x="0%"
							y="0%"
							width="100%"
							height="100%"
							result="turbulence"
						/><feGaussianBlur
							stdDeviation="20 0"
							x="0%"
							y="0%"
							width="100%"
							height="100%"
							in="turbulence"
							result="blur"
						/><feBlend
							mode="color-dodge"
							x="0%"
							y="0%"
							width="100%"
							height="100%"
							in="SourceGraphic"
							in2="blur"
							result="blend"
						/></filter
					></defs
				><path fill="url(#a)" filter="url(#b)" d="M0 0h700v700H0z" /></svg
			>
		</aside>

		<div
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
						<div class="flex items-center gap-x-4 h-20">
							<Arrows {back} {forward} />
							<Search />
						</div>
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
							<Virtualist itemHeight={24} class="flex flex-col w-full mt-2 h-full" />
						</ul>
					</div>
				</div>
			</div>
			<Footer />
		</div>
	{/if}
</div>
