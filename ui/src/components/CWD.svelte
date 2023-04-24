<script lang="ts">
	import { events } from '../event'
	import { cwd, cwdSplit, historyIndex, refreshExplorer, selected } from '../store'
	import { outsideClick } from '../utils'
	import ArrowLeft from './icons/ArrowLeft.svelte'
	import Reload from './icons/Reload.svelte'

	let searchNode: HTMLButtonElement
	let inputSearchNode: HTMLInputElement

	let isSearchSelected = false

	// Focus search input when search button is clicked
	$: if (inputSearchNode) {
		inputSearchNode.focus()
	}

	// Close search when clicking outside
	$: if (searchNode) {
		outsideClick(searchNode, () => {
			isSearchSelected = false
		})
	}
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
			<ul class="flex">
				{#each $cwdSplit as dir, i}
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
						{#if i < $cwdSplit.length - 1}
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
