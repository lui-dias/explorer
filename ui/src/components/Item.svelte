<script lang="ts">
	import { onMount } from 'svelte'

	import { isMultipleSelected, selected } from '../store'
	import type { ExplorerItem } from '../types'

	import { events } from '../event'
	import { __pywebview, formatBytes, outsideClick, setPath } from '../utils'
	import Icon from './Icon.svelte'

	export let file: ExplorerItem
	let size = file.size ?? '0 B'
	let itemNode: HTMLButtonElement
	let inputEditNode: HTMLInputElement

	$: if (size) {
		file.size = size
	}

	async function executeEdit() {
		const path = `${file.parent}/${file.name}`
		const exists = await __pywebview.exists(path)

		if (file.name === '') {
			events.emit('footer_text', {
				text: 'The name cannot be empty',
				type: 'error',
			})
		} else if (exists) {
			events.emit('footer_text', {
				text: `'${file.name}' already exists`,
				type: 'error',
			})
		} else {
			if (file.action === 'create_file') {
				events.emit('create_file', path)
			} else if (file.action === 'create_folder') {
				events.emit('create_folder', path)
			} else if (file.action === 'rename') {
				events.emit('rename', file.path, path)
			}
		}
	}

	onMount(async () => {
		outsideClick(itemNode, () => {
			if (!$isMultipleSelected) {
				file.isEditMode = false
			}
		})

		while (true) {
			const { size: newSize, end } = await __pywebview.stream_folder_size(file.path)

			size = newSize

			if (end) break
		}
	})

	$: if (file.isEditMode && inputEditNode) {
		inputEditNode.focus()
	}
</script>

<button
	class={`_item flex items-center w-full hover:bg-[#7f8388]/20 hover:font-bold cursor-pointer outline-none ${
		$selected.find(item => item.path === file.path) ? 'bg-purple-300/20' : ''
	}`}
	bind:this={itemNode}
	on:click={() => {
		selected.set($isMultipleSelected ? [...$selected, file] : [file])
        events.emit('itemClick')
	}}
	on:dblclick={() => {
        if (file.kind === 'folder') {
            setPath(file.path)
		}
        events.emit('itemDoubleClick')
	}}
>
	<div class="w-[50%]">
		{#if file.isEditMode}
			<input
				type="text"
				class="w-full h-full px-2 rounded-md outline-none dark:bg-transparent"
				spellcheck="false"
				autocomplete="false"
				bind:value={file.name}
				bind:this={inputEditNode}
				on:blur={executeEdit}
				on:keydown={e => {
					if (e.key === 'Enter') {
						executeEdit()
					}
				}}
				on:focus={() => {
					inputEditNode.setSelectionRange(0, inputEditNode.value.length)
				}}
			/>
		{:else}
			<div class="text-[#b9b9b9] flex items-center gap-x-1.5 w-64 text-sm" title={file.path}>
				<Icon icon={file} />
				<span class="w-full overflow-hidden text-ellipsis whitespace-nowrap text-start">
					{file.name}
				</span>
			</div>
		{/if}
	</div>

	<span class="text-[#b9b9b9] text-sm text-start w-[20%]">
		{file.modified}
	</span>
	<span class="text-[#b9b9b9] text-sm capitalize text-start w-[15%]">
		{#if file.kind === 'folder'}
			Folder
		{:else}
			{file.kind}
		{/if}
	</span>
	<span class="text-[#b9b9b9] text-sm text-right w-[15%]">
		{formatBytes(size)}
	</span>
</button>
