<script lang="ts">
	import { onMount } from 'svelte'
	import VirtualList from 'svelte-tiny-virtual-list'
	import { explorerItems, isSearching, scrollExplorerToEnd, searchItems } from '../store'
	import type { ExplorerItem } from '../types'
	import Item from './Item.svelte'
	import Loading from './Loading.svelte'

	let height = 0
	let items = [] as ExplorerItem[]
	let itemPos = 0

	scrollExplorerToEnd.set(() => {
		itemPos = items.length - 1
	})

	onMount(() => {
		const wh = window.innerHeight

		const windowButtons = document.getElementById('window-buttons')!
		const cwd = document.getElementById('cwd')!
		const actions = document.getElementById('actions')!

		const wbH = windowButtons.getBoundingClientRect().height
		const cwdH = cwd.getBoundingClientRect().height
		const actionsH = actions.getBoundingClientRect().height
		const footerH = 40

		const cwdMargin = 12 * 2
		const headersH = 24

		height = wh - wbH - cwdH - actionsH - footerH - cwdMargin - headersH
	})

	$: {
		if ($searchItems.length) {
			items = $searchItems
		} else {
			items = $explorerItems
		}
	}
</script>

{#if items.length === 0}
	{#if $isSearching}
		{#if items.length === 0}
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
	{/if}
{:else}
	<div data-test-id="vl" class="[&>*]:pr-2 [&>*]:scrollbar-thin [&>*]:scrollbar-thumb-zinc-700">
		<VirtualList
			width="100%"
			{height}
			itemCount={items.length}
			itemSize={24}
			scrollToIndex={itemPos}
		>
			<li slot="item" class="absolute w-full" let:index let:style {style}>
				<Item file={items[index]} />
			</li>
		</VirtualList>
	</div>
{/if}
