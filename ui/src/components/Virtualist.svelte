<script lang="ts">
	import { onMount } from 'svelte'
	import { explorerItems, scrollExplorerToEnd, searchItems } from '../store'
	import { isClient } from '../utils'
	import Item from './Item.svelte'
	import type { ExplorerItem } from '../types'

	export let itemHeight: number = 0

	let list: HTMLDivElement
	let scrollTop = 0
	let endIndex = 0
	let renderIndex = [] as number[]
	let items = [] as ExplorerItem[]

	let innerHeight = items.length * itemHeight
	let startIndex = Math.floor(scrollTop / itemHeight)

	scrollExplorerToEnd.set(() => {
		scrollTop = items.length * itemHeight
	})

	$: {
		if (isClient()) {
			const endIndex = Math.min(
				items.length - 1,
				Math.floor((scrollTop + window.innerHeight) / itemHeight),
			)

			renderIndex = []
			for (let i = startIndex; i <= endIndex; i++) {
				renderIndex.push(i)
			}
			renderIndex = [...renderIndex]
		}
	}

	$: if ($explorerItems) {
		items = $explorerItems
	}

	$: if ($searchItems) {
		items = $searchItems
	}

	onMount(() => {
		endIndex = Math.min(
			items.length - 1,
			Math.floor((scrollTop + window.innerHeight) / itemHeight),
		)

		for (let i = startIndex; i <= endIndex; i++) {
			renderIndex.push(i)
		}
		renderIndex = [...renderIndex]
	})
</script>

<div
	class={`${$$props.class} relative overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 pr-2`}
	bind:this={list}
	on:scroll={() => (scrollTop = list.scrollTop)}
>
	{#if items.length === 0}
		<div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col">
			<p class="text-center text-zinc-200 font-medium text-3xl">Nothing found...</p>
			<p class="text-center text-zinc-500 text-lg whitespace-nowrap">Check back later, maybe something will show up</p>
			<p class="text-center text-zinc-500 text-3xl mt-2">😭</p>
		</div>
	{:else}
		<div class="relative" style={`height: ${innerHeight}px`}>
			{#each renderIndex as index}
				<li class="absolute w-full" style={`top: ${index * itemHeight}px`}>
					<Item file={items[index]} />
				</li>
			{/each}
		</div>
	{/if}
</div>
