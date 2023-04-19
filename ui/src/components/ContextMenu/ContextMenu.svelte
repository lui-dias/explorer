<script lang="ts">
	import { onMount } from 'svelte'
	import { outsideClick } from '../../utils'
	import ContextMenuItem from './ContextMenuItem.svelte'
	import SortInner from './Sort/SortInner.svelte'
	import SortItem from './Sort/SortItem.svelte'
	import { contextMenuOpen, selectedItem } from '../../stores/explorerStore'
	import NewItem from './New/NewItem.svelte'
	import NewInner from './New/NewInner.svelte'

	let contextMenuNode: HTMLMenuElement
	let parentHeight = 0

	onMount(() => {
		parentHeight = contextMenuNode.getBoundingClientRect().height

		outsideClick(contextMenuNode, () => {
			contextMenuOpen.set(false)
		})
	})
</script>

<svelte:window
	on:keyup={e => {
		if (e.key === 'Escape') {
			contextMenuOpen.set(false)
		}
	}}
	on:contextmenu={e => {
		e.preventDefault()

		let x = e.clientX
		let y = e.clientY

		const ww = window.innerWidth
		const wh = window.innerHeight

		const bounds = contextMenuNode.getBoundingClientRect()

		const cw = bounds.width
		const ch = bounds.height

		if (x + cw > ww) {
			x = ww - cw
		}

		if (y + ch > wh) {
			y = wh - ch
		}

		contextMenuNode.style.left = x + 'px'
		contextMenuNode.style.top = y + 'px'

		contextMenuOpen.set(true)
	}}
/>

<menu
	class="flex flex-col absolute dark:bg-zinc-600 dark:text-purple-100 z-10"
	bind:this={contextMenuNode}
	class:invisible={!$contextMenuOpen}
>
	<li class="dark:hover:bg-zinc-600">
		{#if $selectedItem}
			<ContextMenuItem {parentHeight}>
				<NewItem slot="item" />
                <NewInner slot="inner" />
			</ContextMenuItem>
		{:else}
			<ContextMenuItem {parentHeight}>
				<SortItem slot="item" />
				<SortInner slot="inner" />
			</ContextMenuItem>
		{/if}
	</li>
</menu>
