<script lang="ts">
	import { onMount } from 'svelte'
	import { events } from '../event'
	import {
		cwd,
		explorerItems,
		footer,
		history,
		historyIndex,
		isMultipleSelected,
		refreshExplorer,
		selectedItem,
		sortType,
	} from '../store'
	import type { TFooter, TSortTypes } from '../types'
	import { __pywebview, debounce, gen_id, isNumber, outsideClick, sort } from '../utils'
	import ContextMenu from './ContextMenu/ContextMenu.svelte'
	import Loading from './Loading.svelte'
	import Virtualist from './Virtualist.svelte'
	import ArrowLeft from './icons/ArrowLeft.svelte'
	import Close from './icons/Close.svelte'
	import Error from './icons/Error.svelte'
	import Info from './icons/Info.svelte'
	import Maximize from './icons/Maximize.svelte'
	import Minimize from './icons/Minimize.svelte'
	import Reload from './icons/Reload.svelte'
	import Warning from './icons/Warning.svelte'

	let cwdSplit = [] as string[]

	let isSearchSelected = false
	let searchNode: HTMLButtonElement
	let inputSearchNode: HTMLInputElement
	let explorerItemsNode: HTMLUListElement

	let isLoading = true
	let footerDebounce = debounce(
		() =>
			footer.set({
				text: '',
				type: 'none',
			}),
		5000,
	)

	events.on('create_file', async (file: string) => {
		console.log('create_file')

		await __pywebview.create_file(file)
        events.emit('full_reload')
	})
	events.on('create_folder', async (folder: string) => {
        console.log('create_folder')
        
		await __pywebview.create_folder(folder)
        events.emit('full_reload')
	})
	events.on('rename', async (from: string, to: string) => {
        console.log('rename')
        
		await __pywebview.rename(from, to)
        events.emit('full_reload')
	})
	events.on('delete', async (path: string | string[], moveToTrash: boolean) => {
		const id = gen_id()

		while (true) {
			const { end, total, deleted } = await __pywebview.stream_delete(id, path, moveToTrash)
			events.emit('footer_text', {
				text: `Deleted ${deleted}/${total}`,
				type: 'info',
			})

			if (end) {
				break
			}
		}

		events.emit('full_reload')
	})
	events.on('full_reload', async () => {
		cwdSplit = $cwd.split('/')
		explorerItems.set([])
		explorerItems.set(await __pywebview.ls($cwd))
		sortItems()
	})

	events.on('footer_text', ({ text, type }: TFooter) => {
		footer.set({
			text,
			type,
		})

		footerDebounce()
	})

	function sortItems() {
		if ($sortType === 'name') {
			explorerItems.set(
				sort($explorerItems, i => (isNumber(i.name) ? Number(i.name) : i.name)),
			)
		} else if ($sortType === 'modified') {
			explorerItems.set(sort($explorerItems, i => i.modified))
		} else if ($sortType === 'type') {
			explorerItems.set(sort($explorerItems, i => i.kind))
		} else if ($sortType === 'size') {
			// FIXME: not working
			explorerItems.set(sort($explorerItems, i => i.size))
		}
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
		await __pywebview.__wait()

		console.log('ready')
		sortType.set((localStorage.getItem('sortType') || $sortType) as TSortTypes)
		cwd.set(localStorage.getItem('cwd') || (await __pywebview.home()))

		const h = [] as string[]

		const cwdSplit = $cwd.split('/')
		for (let i = 0; i < cwdSplit.length; i++) {
			h.push(cwdSplit.slice(0, i + 1).join('/'))
		}
		history.set(h)
		historyIndex.set(h.length - 1)

		sortType.subscribe(v => {
			sortItems()

			localStorage.setItem('sortType', $sortType)
		})

		cwd.subscribe(v => {
			if (v) {
				localStorage.setItem('cwd', $cwd)
				events.emit('full_reload')
			}
		})

		historyIndex.subscribe(v => {
			cwd.set($history[$historyIndex])
		})

		outsideClick(searchNode, () => {
			isSearchSelected = false
		})

		outsideClick(explorerItemsNode, () => {
			selectedItem.set([])
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
	on:keydown={async e => {
		if (e.key === 'Escape') {
			isSearchSelected = false
			selectedItem.set([])
		}

		if (e.key === 'Control') {
			isMultipleSelected.set(true)
		}

		if ($selectedItem.length) {
			if (e.key === 'F2') {
				if ($selectedItem.length > 1) {
					events.emit('footer_text', {
						text: 'Cannot rename multiple items',
						type: 'warning',
					})
					return
				}

				explorerItems.set(
					$explorerItems.map(i => {
						if (!$selectedItem) {
							return i
						}

						if (i.path === $selectedItem[0].path) {
							return {
								...i,
								isEditMode: true,
								action: 'rename',
							}
						}

						return i
					}),
				)
			} else if (e.key === 'Delete') {
				events.emit(
					'delete',
					$selectedItem.map(i => i.path),
					!e.shiftKey,
				)
				events.emit('full_reload')
			}
		}
	}}
/>

<ContextMenu />

<div class="w-full h-full dark:bg-zinc-800 flex flex-col gap-y-2">
	<div class="flex justify-end">
		<button type="button" class="hover:bg-zinc-700 py-2 px-4" on:click={__pywebview.minimize}>
			<Minimize class="fill-purple-200" />
		</button>
		<button type="button" class="hover:bg-zinc-700 py-2 px-4" on:click={__pywebview.maximize}>
			<Maximize class="fill-purple-200" />
		</button>
		<button type="button" class="hover:bg-red-500 py-2 px-4" on:click={__pywebview.close}>
			<Close class="fill-purple-200" />
		</button>
	</div>
	{#if isLoading}
		<Loading />
	{:else}
		<div class="flex gap-x-2 mx-3 mt-3">
			<div class="flex gap-x-3">
				<button type="button" class="w-3" disabled={$historyIndex === 0} on:click={back}>
					<ArrowLeft />
				</button>

				<button
					type="button"
					class="transform rotate-180 w-3"
					disabled={$historyIndex === $history.length - 1}
					on:click={forward}
				>
					<ArrowLeft />
				</button>
			</div>

			<button
				type="button"
				class="dark:bg-zinc-700 w-full dark:text-violet-300 flex items-center overflow-x-auto"
				on:focus={() => {
					isSearchSelected = true
				}}
				bind:this={searchNode}
			>
				{#if isSearchSelected}
					<!-- svelte-ignore a11y-autofocus -->
					<input
						type="text"
						class="bg-transparent w-full h-full px-4 outline-none focus:outline-purple-300"
						autofocus
						value={$cwd}
						on:keyup={async e => {
							if (e.key === 'Enter') {
								cwd.set(inputSearchNode.value)
								$refreshExplorer()
							}
						}}
						bind:this={inputSearchNode}
					/>
				{:else}
					<div class="relative w-full">
						<ul class="flex">
							{#each cwdSplit as dir, i}
								<li class="flex items-center">
									<button
										type="button"
										class="dark:hover:bg-purple-300/20 p-2"
										on:click={() => {
											historyIndex.set($historyIndex - 1)
										}}
									>
										<span class="text-gray-500 dark:text-violet-200">{dir}</span
										>
									</button>
									{#if i < cwdSplit.length - 1}
										<span class="transform rotate-180 w-1.5 block mx-1">
											<ArrowLeft />
										</span>
									{/if}
								</li>
							{/each}
						</ul>
						<button
							type="button"
							class="absolute inset-y-0 right-2"
							on:click={$refreshExplorer}
						>
							<Reload />
						</button>
					</div>
				{/if}
			</button>
		</div>

		<div class="flex mx-3">
			<span class="dark:text-purple-100 text-left border-r border-purple-100 text-sm w-[50%]"
				>Name</span
			>
			<span
				class="dark:text-purple-100 text-left border-r border-purple-100 pl-2 text-sm w-[20%]"
				>Modified</span
			>
			<span
				class="dark:text-purple-100 text-left border-r border-purple-100 pl-2 text-sm w-[15%]"
				>Type</span
			>
			<span
				class="dark:text-purple-100 text-left border-r border-purple-100 pl-2 text-sm w-[15%]"
				>Size</span
			>
		</div>
		<ul bind:this={explorerItemsNode} class="h-[calc(100%-40px-40px)] mx-3">
			<Virtualist itemHeight={24} class="flex flex-col w-full mt-2 h-full" />
		</ul>

		<footer
			class="h-10 px-2 text-purple-300 border-t border-zinc-700 flex items-center gap-x-2"
		>
			{#if $footer.type !== 'none'}
				{#if $footer.type === 'info'}
					<Info class="fill-purple-200" />
				{/if}
				{#if $footer.type === 'warning'}
					<Warning class="fill-purple-200" />
				{/if}
				{#if $footer.type === 'error'}
					<Error class="fill-purple-200" />
				{/if}
			{/if}

			{$footer.text}
		</footer>
	{/if}
</div>
