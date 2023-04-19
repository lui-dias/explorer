<script lang="ts">
	import { onMount } from 'svelte'
	import { explorerItems } from '../store'
	import Item from './Item.svelte'

	export let itemHeight: number = 0
	let list: HTMLDivElement

	let scrollTop = 0

	let innerHeight = $explorerItems.length * itemHeight
	let startIndex = Math.floor(scrollTop / itemHeight)
	let endIndex = 0
	let renderIndex = [] as number[]

	$: {
		if (typeof window !== 'undefined') {
			const endIndex = Math.min(
				$explorerItems.length - 1,
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
			$explorerItems.length - 1,
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
	on:scroll={() => (scrollTop = list.scrollTop)}
>
	<div class="relative" style={`height: ${innerHeight}px`}>
		{#each renderIndex as index}
			<li class="absolute w-full" style={`top: ${index * itemHeight}px`}>
				<Item file={$explorerItems[index]} />
			</li>
		{/each}
	</div>
</div>
