<script lang="ts">
	import { onMount } from 'svelte'
	import { explorerItems, isSearching, scrollExplorerToEnd, searchItems } from '../store'
	import { isClient } from '../utils'
	import Item from './Item.svelte'
	import type { ExplorerItem } from '../types'
	import Loading from './Loading.svelte'

	export let itemHeight: number = 0

	let list: HTMLDivElement
	let scrollTop = 0
	let endIndex = 0
	let renderIndex = [] as number[]
	let items = [] as ExplorerItem[]

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
		{#if $isSearching && $explorerItems.length === 0}
			<Loading />
		{:else}
			<div
				class="absolute flex flex-col transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2"
			>
				<p class="text-3xl font-medium text-center text-zinc-200">Nothing found...</p>
				<p class="text-lg text-center text-zinc-500 whitespace-nowrap">
					Come back later, maybe something will show up
				</p>
				<p class="mt-2 text-3xl text-center text-zinc-500">😭</p>
			</div>
		{/if}
	{:else}
		<div class="relative">
			{#each renderIndex as index}
				<li class="absolute w-full" style={`top: ${index * itemHeight}px`}>
					<Item file={items[index]} />
				</li>
			{/each}
		</div>
	{/if}
</div>
