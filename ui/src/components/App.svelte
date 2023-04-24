<script lang="ts">
	import { onMount } from 'svelte'
	import { events } from '../event'
	import {
		cwd,
		cwdSplit,
		explorerItems,
		footer,
		history,
		historyIndex,
		isMultipleSelected,
		selected,
		sortType,
	} from '../store'
	import type { ExplorerItem, TFooter, TSortTypes } from '../types'
	import { __pywebview, debounce, gen_id, isNumber, sort } from '../utils'
	import ContextMenu from './ContextMenu/ContextMenu.svelte'
	import Footer from './Footer.svelte'
	import Loading from './Loading.svelte'
	import QuickAccess from './QuickAccess.svelte'
	import Settings from './Settings.svelte'
	import Virtualist from './Virtualist.svelte'
	import ArrowLeft from './icons/ArrowLeft.svelte'
	import Close from './icons/Close.svelte'
	import Maximize from './icons/Maximize.svelte'
	import Minimize from './icons/Minimize.svelte'
	import Cwd from './CWD.svelte'

	let explorerItemsNode: HTMLUListElement

	let isLoading = true

	// Without this, the footer will be cleared after 5 seconds
	// even if other events are emitted
	let footerDebounce = debounce(
		() =>
			footer.set({
				text: '',
				type: 'none',
			}),
		5000,
	)

	events.on('create_file', async (file: string) => {
		await __pywebview.create_file(file)
		events.emit('reload')
	})

	events.on('create_folder', async (folder: string) => {
		await __pywebview.create_folder(folder)
		events.emit('reload')
	})

	events.on('rename', async (from: string, to: string) => {
		await __pywebview.rename(from, to)
		events.emit('reload')
	})

	events.on('delete', async (path: string | string[], moveToTrash: boolean) => {
		const id = gen_id()

		while (true) {
			const { end, total, deleted, last_deleted } = await __pywebview.stream_delete(
				id,
				path,
				moveToTrash,
			)
			events.emit('footer_text', {
				text: `Deleted ${deleted}/${total} ${!!last_deleted ? `- ${last_deleted}` : ''}`,
				type: 'info',
			})

			if (end) {
				break
			}
		}

		events.emit('reload')
		selected.set([])
	})

	events.on('reload', async () => {
		cwdSplit.set($cwd.split('/'))

		// When creating a file/folder, even using ls, the size of the files was buggy,
		// a file had the size of another file
		// Doing this causes a small flash in explorer, but it solves the problem :/
		explorerItems.set([])
		explorerItems.set(sortItems(await __pywebview.ls($cwd)))
	})

	events.on('footer_text', ({ text, type }: TFooter) => {
		footer.set({
			text,
			type,
		})

		footerDebounce()
	})

	function sortItems(items: ExplorerItem[]) {
		if ($sortType === 'name') {
			return sort(items, i => (isNumber(i.name) ? Number(i.name) : i.name))
		}
		if ($sortType === 'modified') {
			return sort(items, i => i.modified)
		}
		if ($sortType === 'type') {
			return sort(items, i => i.kind)
		}
		if ($sortType === 'size') {
			return sort(items, i => i.size)
		}

		return items
	}

	function back() {
		if ($historyIndex > 0) {
			historyIndex.set($historyIndex - 1)
		}
	}

	function forward() {
		if ($historyIndex < $history.length - 1) {
			historyIndex.set($historyIndex + 1)
		}
	}

	onMount(async () => {
		// Wait pywebview to be ready
		await __pywebview.__wait()
		console.log('ready')

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

		sortType.subscribe(v => {
			explorerItems.set(sortItems($explorerItems))

			localStorage.setItem('sortType', $sortType)
		})

		cwd.subscribe(v => {
			if (v) {
				localStorage.setItem('cwd', $cwd)
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
	class="w-full h-full dark:bg-zinc-800 flex flex-col gap-y-2"
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
	}}
>
	{#if isLoading}
		<Loading />
	{:else}
		<div class="flex justify-end">
			<button
				type="button"
				class="hover:bg-zinc-700 py-2 px-4"
				on:click={__pywebview.minimize}
			>
				<Minimize class="fill-primary" />
			</button>
			<button
				type="button"
				class="hover:bg-zinc-700 py-2 px-4"
				on:click={__pywebview.maximize}
			>
				<Maximize class="fill-primary" />
			</button>
			<button type="button" class="hover:bg-red-500 py-2 px-4" on:click={__pywebview.close}>
				<Close class="fill-primary" />
			</button>
		</div>

		<div class="flex items-center pr-3">
			<div class="flex gap-x-2 mx-3">
				<div class="flex gap-x-3">
					<button
						type="button"
						class="w-3"
						disabled={$historyIndex === 0}
						on:click={back}
					>
						<ArrowLeft class="fill-primary" />
					</button>

					<button
						type="button"
						class="transform rotate-180 w-3"
						disabled={$historyIndex === $history.length - 1}
						on:click={forward}
					>
						<ArrowLeft class="fill-primary" />
					</button>
				</div>
			</div>

			<Cwd />
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
				<ul bind:this={explorerItemsNode} class="h-[calc(100%-40px-40px)] mx-3">
					<Virtualist itemHeight={24} class="flex flex-col w-full mt-2 h-full" />
				</ul>
			</div>
		</div>

		<Footer />
	{/if}
</div>
