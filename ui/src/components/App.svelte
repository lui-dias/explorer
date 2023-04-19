<script lang="ts">
	import { onMount } from 'svelte'
	import { events } from '../event'
	import {
		cwd,
		explorerItems,
		footerText,
		history,
		historyIndex,
		refreshExplorer,
		selectedItem,
		sortType,
	} from '../store'
	import type { TSortTypes } from '../types'
	import { __pywebview, isNumber, outsideClick, sort } from '../utils'
	import ContextMenu from './ContextMenu/ContextMenu.svelte'
	import Virtualist from './Virtualist.svelte'
	import ArrowLeft from './icons/ArrowLeft.svelte'
	import Reload from './icons/Reload.svelte'

	let cwdSplit = [] as string[]

	let isSearchSelected = false
	let searchNode: HTMLButtonElement
	let inputSearchNode: HTMLInputElement
	let explorerItemsNode: HTMLUListElement

	events.on('create_file', async (file: string) => {
		console.log('create_file')

		await __pywebview.create_file(file)
	})
	events.on('create_folder', async (folder: string) => {
		console.log('create_folder')

		await __pywebview.create_folder(folder)
	})
	events.on('rename', async (from: string, to: string) => {
		console.log('rename')

		await __pywebview.rename(from, to)
	})
	events.on('delete', async (path: string, moveToTrash: boolean) => {
		while (true) {
			const { end, total, deleted } = await __pywebview.stream_delete(path, moveToTrash)
			console.log(`Deleted ${deleted} of ${total} files`)

			if (end) {
				break
			}
		}
	})
	events.on('full_reload', async () => {
		explorerItems.set(await __pywebview.ls($cwd))
	})
	events.on('reset_delete', async (path: string) => {
		await __pywebview.reset_stream_delete(path)
	})
	events.on('reset_size', async (path: string) => {
		// @ts-ignore
		await __pywebview.reset_stream_size(path)
	})

	footerText.subscribe(v => {
		setTimeout(() => {
			footerText.set('')
		}, 5000)
	})

	refreshExplorer.set(async () => {
		cwdSplit = $cwd.split('/')
		explorerItems.set(
			(await __pywebview.ls($cwd)).map(i => ({
				...i,
				isEditMode: false,
			})),
		)

		sortItems()
	})

	async function isPywebviewReady() {
		// @ts-ignore
		if (typeof pywebview === 'undefined') {
			return new Promise(resolve => {
				setTimeout(() => {
					resolve(isPywebviewReady())
				}, 100)
			})
		}

		return true
	}

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

	onMount(() => {
		isPywebviewReady().then(async () => {
			console.log('ready')
			sortType.set((localStorage.getItem('sortType') || $sortType) as TSortTypes)
			// @ts-ignore
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
					$refreshExplorer()

					localStorage.setItem('cwd', $cwd)
				}
			})

			historyIndex.subscribe(v => {
				cwd.set($history[$historyIndex])
			})
		})

		outsideClick(searchNode, () => {
			isSearchSelected = false
		})

		outsideClick(explorerItemsNode, () => {
			selectedItem.set(null)
		})
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
	on:keydown={async e => {
		if (e.key === 'Escape') {
			isSearchSelected = false
			selectedItem.set(null)
		}

		if ($selectedItem) {
			if (e.key === 'F2') {
				explorerItems.set(
					$explorerItems.map(i => {
						if (!$selectedItem) {
							return i
						}

						if (i.path === $selectedItem.path) {
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
				events.emit('delete', $selectedItem.path, !e.shiftKey)
				events.emit('full_reload')
				events.emit('reset_delete', $selectedItem.path)
			}
		}
	}}
/>

<ContextMenu />

<div class="w-full h-full dark:bg-zinc-800 flex flex-col gap-y-2">
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
									<span class="text-gray-500 dark:text-violet-200">{dir}</span>
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
		<span class="dark:text-purple-100 text-left border-r border-purple-100 pl-2 text-sm w-[20%]"
			>Modified</span
		>
		<span class="dark:text-purple-100 text-left border-r border-purple-100 pl-2 text-sm w-[15%]"
			>Type</span
		>
		<span class="dark:text-purple-100 text-left border-r border-purple-100 pl-2 text-sm w-[15%]"
			>Size</span
		>
	</div>
	<ul bind:this={explorerItemsNode} class="h-[calc(100%-40px-40px)] mx-3">
		<Virtualist itemHeight={24} class="flex flex-col w-full mt-2 h-full" />
	</ul>

	<footer class="h-10 px-2 text-purple-300 border-t border-zinc-700 flex items-center">
		{$footerText}
	</footer>
</div>
