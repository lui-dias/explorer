<script lang="ts">
	import { onMount } from 'svelte'
	import { E } from '../../event'
	import {
		contextMenuOpen,
		cwd,
		installedApps,
		quickAccess,
		selected,
		selectedQuickAccess,
		sortType,
		sortTypeReversed,
	} from '../../store'
	import { outsideClick, py } from '../../utils'
	import Properties from '../Properties.svelte'
	import ContextMenuItem from './ContextMenuItem.svelte'

	let contextMenuNode: HTMLMenuElement
	let propertiesNode: HTMLDialogElement
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
			action: async () => {
				quickAccess.set([...$quickAccess, $selected[0]])
				await py.set('quickAccess', JSON.stringify($quickAccess.map(item => item.path)))

				contextMenuOpen.set(false)
			},
		},
		unpin: {
			text: 'Unpin from Quick Access',
			icon: 'OtherUnpin',
			action: async () => {
				if ($selectedQuickAccess) {
					quickAccess.set([
						...$quickAccess.filter(
							i => $selectedQuickAccess && i.path !== $selectedQuickAccess.path,
						),
					])
				} else {
					quickAccess.set([...$quickAccess.filter(i => i.path !== $selected[0].path)])
				}
				await py.set('quickAccess', JSON.stringify($quickAccess.map(item => item.path)))
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
					action: () => {
						E.createNewExplorerFile()
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Folder',
					icon: 'OtherNewFolder',
					action: () => {
						E.createNewExplorerFolder()
						contextMenuOpen.set(false)
					},
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
					selected: () => $sortType === 'name',
					action: () => {
						sortType.set('name')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Modified',
					icon: 'OtherCalendar',
					selected: () => $sortType === 'modified',
					action: () => {
						sortType.set('modified')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Size',
					icon: 'OtherSize',
					selected: () => $sortType === 'size',
					action: () => {
						sortType.set('size')
						contextMenuOpen.set(false)
					},
				},
				{
					text: 'Type',
					icon: 'OtherTypes',
					selected: () => $sortType === 'type',
					action: () => {
						sortType.set('type')
						contextMenuOpen.set(false)
					},
					dividerBelow: true,
				},
				{
					text: 'Asc',
					icon: 'OtherAsc',
					selected: () => $sortTypeReversed === false,
					action: () => {
						sortTypeReversed.set(false)
						contextMenuOpen.set(false)
					},
					__useStroke: true,
				},
				{
					text: 'Desc',
					icon: 'OtherDesc',
					selected: () => $sortTypeReversed === true,
					action: () => {
						sortTypeReversed.set(true)
						contextMenuOpen.set(false)
					},
					__useStroke: true,
				},
			],
		},
		vscode: {
			text: 'Open in VSCode',
			icon: 'OtherVscode',
			condition: () => $installedApps.some(i => i.name === 'Visual Studio Code'),
			action: async () => {
				await py.shell(
					`"${$installedApps.find(i => i.name === 'Visual Studio Code')!.exePath}" ${
						$selected[0].path
					}`,
				)
				contextMenuOpen.set(false)
			},
		},
        terminal: {
            text: 'Open in Terminal',
            icon: 'OtherTerminal',
            action: async () => {
                await py.shell(`%localappdata%\\Microsoft\\WindowsApps\\wt.exe -d ${$cwd}`)
                contextMenuOpen.set(false)
            }
        },
		properties: {
			text: 'Properties',
			icon: 'OtherInfo',
			action: () => {
				propertiesNode.showModal()
				contextMenuOpen.set(false)
			},
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

<Properties bind:propertiesNode file={$selected[0]} />

<menu
	class="neuBorder absolute z-20 flex flex-col bg-[#383e45] dark:text-purple-100"
	class:invisible={!$contextMenuOpen}
	data-test-id="contextmenu"
	bind:this={contextMenuNode}
>
	<li class="dark:bg-[#32373e]">
		{#if $selectedQuickAccess}
			<ContextMenuItem {parentHeight} {...components.unpin} />
		{:else if $selected.length}
			{#if $selected.length === 1}
				{#if $selected[0].kind === 'folder'}
					{#if $quickAccess.some(i => i.path === $selected[0].path)}
						<ContextMenuItem {parentHeight} {...components.unpin} />
					{:else}
						<ContextMenuItem {parentHeight} {...components.pin} />
					{/if}
				{/if}
				<ContextMenuItem
					{parentHeight}
					{...components.vscode}
					iconClass="[&_.vscode-color]:fill-primary"
				/>
			{/if}
			<ContextMenuItem {parentHeight} {...components.properties} />
		{:else}
			<ContextMenuItem {parentHeight} {...components.new} />
			<ContextMenuItem {parentHeight} {...components.sort} />
			<ContextMenuItem {parentHeight} {...components.terminal} />
		{/if}
	</li>
</menu>
