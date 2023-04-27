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
	let isConfigLoaded = false

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

		isConfigLoaded = true

		console.log(config)

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

{#if isConfigLoaded}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div
		class="w-full h-full dark:bg-background flex flex-col gap-y-2"
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
			<WindowButtons />

			<div class="flex items-center pr-3">
				<Arrows {back} {forward} />
				<Cwd />
				<Search />
			</div>

			<div class="flex w-full h-full">
				<QuickAccess />

				<div class="flex flex-col gpa-y-2 w-full h-full">
					<div class="flex mx-3">
						<span
							class="dark:text-text text-left border-r border-purple-100 text-sm w-[50%]"
							>Name</span
						>
						<span
							class="dark:text-text text-left border-r border-purple-100 pl-2 text-sm w-[20%]"
							>Modified</span
						>
						<span
							class="dark:text-text text-left border-r border-purple-100 pl-2 text-sm w-[15%]"
							>Type</span
						>
						<span
							class="dark:text-text text-left border-r border-purple-100 pl-2 text-sm w-[15%]"
							>Size</span
						>
					</div>
					<ul bind:this={explorerItemsNode} class="h-full mx-3">
						<Virtualist itemHeight={24} class="flex flex-col w-full mt-2 h-full" />
					</ul>
				</div>
			</div>

			<Footer />
		{/if}
	</div>
{:else}
	<span />
{/if}
