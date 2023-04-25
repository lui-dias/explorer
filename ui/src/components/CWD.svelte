<script lang="ts">
	import { onMount } from 'svelte'
	import { events } from '../event'
	import { cwd, cwdSplit, history, historyIndex, refreshExplorer, selected } from '../store'
	import { outsideClick, sleep } from '../utils'
	import ArrowLeft from './icons/ArrowLeft.svelte'
	import Reload from './icons/Reload.svelte'

	let searchNode: HTMLButtonElement
	let inputSearchNode: HTMLInputElement
	let cwdList: HTMLUListElement
	let hideNItems = 0

	let isSearchSelected = false

	async function fixHorizontalScroll() {
        if (!cwdList) return

		if (cwdList.scrollWidth <= cwdList.clientWidth) {
			hideNItems = 0
		} else {
			while (cwdList.scrollWidth > cwdList.clientWidth) {
				// This is necessary to avoid infinite loop
				await sleep(0)

				hideNItems += 1
			}
		}
	}

	// Focus search input when search button is clicked
	$: if (inputSearchNode) {
		inputSearchNode.focus()
	}

	$: if ($cwdSplit && cwdList) {
		const observer = new MutationObserver(() => {
			fixHorizontalScroll()

			// Avoid infinite loop when setting hideNItems
			observer.disconnect()
		})
		observer.observe(cwdList, { childList: true })
	}

	onMount(() => {
		fixHorizontalScroll()

		// Close search when clicking outside
		outsideClick(searchNode, () => {
			isSearchSelected = false
		})

		window.addEventListener('resize', () => {
			fixHorizontalScroll()
		})
	})
</script>

<svelte:window
	on:keydown={e => {
		if (e.key === 'Escape') {
			isSearchSelected = false
			selected.set([])
		}
	}}
/>

<button
	type="button"
	class="dark:bg-zinc-700 w-full dark:text-violet-300 flex items-center overflow-x-auto"
	on:focus={() => {
		isSearchSelected = true
	}}
	bind:this={searchNode}
>
	{#if isSearchSelected}
		<input
			type="text"
			class="bg-transparent w-full h-10 px-2 outline-none focus:outline-purple-300"
			value={$cwd}
			on:keyup={async e => {
				if (e.key === 'Enter') {
					cwd.set(inputSearchNode.value)
					events.emit('reload')
				}
			}}
			bind:this={inputSearchNode}
		/>
	{:else}
		<div class="relative w-full">
			<ul class="flex overflow-x-hidden" bind:this={cwdList}>
				{#each $cwdSplit.slice(hideNItems, $cwdSplit.length) as dir, i}
					<li class="flex items-center">
						<button
							type="button"
							class="dark:hover:bg-purple-300/20 p-2"
							on:click={() => {
								const path = $cwdSplit.slice(0, i + 1).join('/')

								history.set([...$history, path])
								historyIndex.set($history.length)
								cwd.set(path)
							}}
						>
							<span class="text-gray-500 dark:text-violet-200 whitespace-nowrap"
								>{dir}</span
							>
						</button>
						{#if dir !== $cwdSplit.slice(-1)[0]}
							<span class="transform rotate-180 w-1.5 block mx-1">
								<ArrowLeft class="fill-primary" />
							</span>
						{/if}
					</li>
				{/each}
			</ul>
			<button type="button" class="absolute inset-y-0 right-2" on:click={$refreshExplorer}>
				<Reload class="stroke-primary" />
			</button>
		</div>
	{/if}
</button>
