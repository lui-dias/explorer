<script lang="ts">
	import { onMount } from 'svelte'
	import { E } from '../../event'
	import {
		contextMenuOpen,
		quickAccess,
		selected,
		selectedQuickAccess,
		sortType,
	} from '../../store'
	import { outsideClick } from '../../utils'
	import ContextMenuItem from './ContextMenuItem.svelte'

	let contextMenuNode: HTMLMenuElement
	let parentHeight = 0

	onMount(() => {
		parentHeight = contextMenuNode.getBoundingClientRect().height

		outsideClick(contextMenuNode, () => {
			contextMenuOpen.set(false)

			if ($selectedQuickAccess) {
				selectedQuickAccess.set(null)
			}
		})
	})

	const components = {
		pin: {
			text: 'Pin to Quick Access',
			icon: 'OtherPin',
			action: () => {
				console.log('inner')
				quickAccess.set([...$quickAccess, $selected[0]])
				localStorage.setItem(
					'quickAccess',
					JSON.stringify($quickAccess.map(item => item.path)),
				)
				contextMenuOpen.set(false)
			},
		},
		unpin: {
			text: 'Unpin from Quick Access',
			icon: 'OtherUnpin',
			action: () => {
				if ($selectedQuickAccess) {
					quickAccess.set([
						...$quickAccess.filter(
							i => $selectedQuickAccess && i.path !== $selectedQuickAccess.path,
						),
					])
				} else {
					quickAccess.set([...$quickAccess.filter(i => i.path !== $selected[0].path)])
				}
				localStorage.setItem(
					'quickAccess',
					JSON.stringify($quickAccess.map(item => item.path)),
				)
				contextMenuOpen.set(false)
			},
		},
		new: {
			text: 'New',
			icon: 'OtherPlus',
			inner: [
				{
					text: 'File',
					icon: 'OtherNewFile',
					action: E.createNewExplorerFile,
				},
				{
					text: 'Folder',
					icon: 'OtherNewFolder',
					action: E.createNewExplorerFolder,
				},
			],
		},
		sort: {
			text: 'Sort',
			icon: 'OtherSort',
			inner: [
				{
					text: 'Name',
					icon: 'OtherAbc',
					selected: $sortType === 'name',
					action: () => {
						sortType.set('name')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Modified',
					icon: 'OtherCalendar',
					selected: $sortType === 'modified',
					action: () => {
						sortType.set('modified')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Size',
					icon: 'OtherSize',
					selected: $sortType === 'size',
					action: () => {
						sortType.set('type')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Type',
					icon: 'OtherTypes',
					selected: $sortType === 'type',
					action: () => {
						sortType.set('size')
						contextMenuOpen.set(false)
					},
				},
			],
		},
	}
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
	class="neuBorder absolute z-20 flex flex-col bg-[#383e45] dark:text-purple-100"
	bind:this={contextMenuNode}
	class:invisible={!$contextMenuOpen}
>
	<li class="dark:bg-[#32373e]">
		{#if $selectedQuickAccess}
			<svelte:component this={ContextMenuItem} {parentHeight} {...components.unpin} />
		{:else if $selected.length}
			<span> Context menu item </span>
			{#if $selected.length === 1 && $selected[0].kind === 'folder'}
				{#if $quickAccess.some(i => i.path === $selected[0].path)}
					<svelte:component this={ContextMenuItem} {parentHeight} {...components.unpin} />
				{:else}
					<svelte:component this={ContextMenuItem} {parentHeight} {...components.pin} />
				{/if}
			{/if}
		{:else}
			<svelte:component this={ContextMenuItem} {parentHeight} {...components.new} />
			<svelte:component this={ContextMenuItem} {parentHeight} {...components.sort} />
		{/if}
	</li>
</menu>
