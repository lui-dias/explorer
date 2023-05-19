<script lang="ts">
	import { onMount } from 'svelte'

	import { explorerItems, isMultipleSelected, selected } from '../store'
	import type { ExplorerItem } from '../types'
	import { asDroppable, asDropZone } from 'svelte-drag-and-drop-actions'

	import { E } from '../event'
	import { py, appendPath, formatBytes, outsideClick } from '../utils'
	import Icon from './ui/Icon.svelte'
	import dayjs from 'dayjs'

	export let file: ExplorerItem
	let size = file.size ?? '0 B'
	let itemNode: HTMLButtonElement
	let inputEditNode: HTMLInputElement
	let n = 0
	let isInside = false

	$: if (size) {
		file.size = size

		// Update selected file, useful to get updated file size on properties
		if ($selected.length === 1 && $selected[0].path === file.path) {
			selected.set([file])
		}
	}

	function removeLastItem() {
		explorerItems.set($explorerItems.slice(0, -1))
	}

	async function executeEdit() {
		const path = `${file.parent}/${file.name}`
		const exists = await py.exists(path)

		if (file.name === '') {
			removeLastItem()
			await E.footerText({
				text: 'The name cannot be empty',
				type: 'error',
			})
		} else if (exists) {
			removeLastItem()
			await E.footerText({
				text: `'${file.name}' already exists`,
				type: 'error',
			})
		} else {
			if (file.action === 'createFile') {
				await E.createFile(path)
			} else if (file.action === 'createFolder') {
				await E.createFolder(path)
			} else if (file.action === 'rename') {
				await E.rename(file.path, path)
			}
		}
	}

	onMount(async () => {
		outsideClick(itemNode, () => {
			if (!$isMultipleSelected) {
				file.isEditMode = false
			}
		})

        await py.startFolderSize(file.path)

		while (true) {
			const r = await py.streamFolderSize(file.path)

            if (!r) break

            const { size: newSize, end } = r

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
		isInside || $selected.find(item => item.path === file.path)
			? 'bg-purple-300/20 font-bold'
			: ''
	}`}
	data-test-id="explorer-item"
	bind:this={itemNode}
	on:click={() => {
		selected.set($isMultipleSelected ? [...$selected, file] : [file])
	}}
	on:dblclick={() => {
		if (file.kind === 'folder') {
			appendPath(file.path)
		}
	}}
	on:dragleave={e => {
		if (file.kind === 'folder') {
			n -= 1

			if (n === 0) {
				isInside = false
			}
		}
	}}
	on:dragenter={e => {
		if (file.kind === 'folder') {
			n += 1
			isInside = true
		}
	}}
	on:drop={e => {
		if (file.kind === 'folder') {
			n -= 1
			isInside = false

			if (n === 0) {
				isInside = false
			}
		}
	}}
	use:asDroppable={{
		DataToOffer: { 'text/plain': file.path },
		Operations: 'copy',
	}}
	use:asDropZone={{
		TypesToAccept: { 'text/plain': 'copy' },
		// @ts-ignore
		onDrop: async (x, y, Operation, data) => {
			if (file.kind === 'folder') {
				const path = Object.values(data)[0]
				// @ts-ignore
				const name = path.split('/').pop()

				// @ts-ignore
				await py.rename(path, `${file.path}/${name}`)

				await E.reload()

				await E.footerText({
					text: `Moved '${name}' to '${file.path}'`,
					type: 'info',
				})
			}
		},
	}}
>
	<div class="w-[50%]">
		{#if file.isEditMode}
			<input
				type="text"
				class="w-full h-full px-2 rounded-md outline-none text-[#b9b9b9] dark:bg-transparent"
				spellcheck="false"
				autocomplete="false"
				data-test-id="edit-file"
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
				<Icon icon={file.type} />
				<span
					class="w-full overflow-hidden text-ellipsis whitespace-nowrap text-start"
					data-test-id="file-name"
				>
					{file.name}
				</span>
			</div>
		{/if}
	</div>

	<span class="text-[#b9b9b9] text-sm text-start w-[20%]">
		{dayjs(file.modified).format('DD/MM/YYYY HH:mm')}
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
