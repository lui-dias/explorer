<script lang="ts">
	import { onMount } from 'svelte'

	import { cwd, history, historyIndex, isMultipleSelected, selected } from '../store'
	import type { ExplorerItem } from '../types'

	import { events } from '../event'
	import { __pywebview, formatBytes, isPathChild, outsideClick, setPath } from '../utils'
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
	class={`_item flex w-full dark:hover:bg-purple-300/20 cursor-pointer outline-none ${
		$selected.find(item => item.path === file.path) ? 'bg-purple-300/20' : ''
	}`}
	bind:this={itemNode}
	on:click={() => {
		selected.set($isMultipleSelected ? [...$selected, file] : [file])
	}}
	on:dblclick={() => {
		if (file.kind === 'folder') {
			setPath(file)
		}
	}}
>
	<div class="w-[50%]">
		{#if file.isEditMode}
			<input
				type="text"
				class="dark:text-text dark:bg-transparent text-gray-900 outline-none rounded-md px-2 h-full w-full"
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
			<div class="dark:text-text flex items-center gap-x-1.5 w-64 text-sm">
				<Icon {file} />
				<span class="overflow-hidden text-ellipsis whitespace-nowrap w-full text-start">
					{file.name}
				</span>
			</div>
		{/if}
	</div>

	<span class="dark:text-text text-sm text-start w-[20%]">
		{file.modified}
	</span>
	<span class="dark:text-text text-sm capitalize text-start w-[15%]">
		{#if file.kind === 'folder'}
			Folder
		{:else}
			{file.kind}
		{/if}
	</span>
	<span class="dark:text-text text-sm text-right w-[15%]">
		{formatBytes(size)}
	</span>
</button>
