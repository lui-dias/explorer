<script lang="ts">
	import { onMount } from 'svelte'
	import type { ExplorerItem } from '../types'

	export let items: ExplorerItem[]
	export let itemHeight: number = 0
	let list: HTMLDivElement

	let scrollTop = 0

	let innerHeight = items.length * itemHeight
	let startIndex = Math.floor(scrollTop / itemHeight)
	let endIndex = 0
	let renderIndex = [] as number[]

	$: {
		if (typeof window !== 'undefined') {
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
	class={`${$$props.class} overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 pr-2`}
	bind:this={list}
	on:scroll={e => (scrollTop = list.scrollTop)}
>
	<div class="relative" style={`height: ${innerHeight}px`}>
		{#each renderIndex as index}
			<li class="absolute w-full" style={`top: ${index * itemHeight}px`}>
				<slot item={items[index]} />
			</li>
		{/each}
	</div>
</div>
