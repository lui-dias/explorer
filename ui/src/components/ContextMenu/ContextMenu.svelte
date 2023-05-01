<script lang="ts">
	import { onMount } from 'svelte'
	import {
		contextMenuOpen,
		cwd,
		explorerItems,
		quickAccess,
		scrollExplorerToEnd,
		selected,
		selectedQuickAccess,
		sortType,
	} from '../../store'
	import { formatDate, outsideClick } from '../../utils'
	import ContextMenuItem from './ContextMenuItem.svelte'

	let contextMenuNode: HTMLMenuElement
	let parentHeight = 0

	onMount(() => {
		parentHeight = contextMenuNode.getBoundingClientRect().height

		outsideClick(contextMenuNode, () => {
			contextMenuOpen.set(false)
		})
	})

	const components = {
		pin: {
			text: 'Pin to Quick Access',
			icon: 'Maximize',
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
			icon: 'Maximize',
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
			icon: 'Plus',
			inner: [
				{
					text: 'File',
					icon: 'NewFile',
					action: () => {
						contextMenuOpen.set(false)

						explorerItems.set([
							...$explorerItems,
							{
								name: 'file',
								path: $cwd + '/file',
								isEditMode: true,
								kind: 'file',
								size: 0,
								parent: $cwd,
								modified: formatDate(new Date()),
								type: 'Text',
								action: 'create_file',
							},
						])

						$scrollExplorerToEnd()
					},
				},
				{
					text: 'Folder',
					icon: 'NewFolder',
					action: () => {
						contextMenuOpen.set(false)

						explorerItems.set([
							...$explorerItems,
							{
								name: 'folder',
								path: $cwd + '/folder',
								isEditMode: true,
								kind: 'folder',
								size: 0,
								parent: $cwd,
								modified: formatDate(new Date()),
								type: 'Folder',
								action: 'create_folder',
							},
						])

						$scrollExplorerToEnd()
					},
				},
			],
		},
		sort: {
			text: 'Sort',
			icon: 'Sort',
			inner: [
				{
					text: 'Name',
					icon: 'Abc',
					selected: $sortType === 'name',
					action: () => {
						sortType.set('name')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Modified',
					icon: 'Calendar',
					selected: $sortType === 'modified',
					action: () => {
						sortType.set('modified')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Size',
					icon: 'Size',
					selected: $sortType === 'size',
					action: () => {
						sortType.set('type')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Type',
					icon: 'Types',
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
	class="absolute z-20 flex flex-col dark:bg-zinc-600 dark:text-purple-100"
	bind:this={contextMenuNode}
	class:invisible={!$contextMenuOpen}
>
	<li class="dark:hover:bg-zinc-600">
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
		<!-- {#if $selectedQuickAccess}

		{:else if $selected.length}
			<span> Context menu item </span>
            {#if $selected.length === 1 && $selected[0].kind === 'folder'}
                {#if $quickAccess.some(i => i.path === $selected[0].path)}
                    <ContextMenuItem {parentHeight}>
                        <UnpinQuickAccessItem slot="item" />
                    </ContextMenuItem>
                {:else}
                    <ContextMenuItem {parentHeight}>
                        <PinQuickAccessItem slot="item" />
                    </ContextMenuItem>
                {/if}
            {/if}
		{:else}
			<ContextMenuItem {parentHeight}>
				<NewItem slot="item" />
				<NewInner slot="inner" />
			</ContextMenuItem>
			<ContextMenuItem {parentHeight}>
				<SortItem slot="item" />
				<SortInner slot="inner" />
			</ContextMenuItem>
		{/if} -->
	</li>
</menu>
