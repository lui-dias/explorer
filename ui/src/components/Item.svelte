<script lang="ts">
	import { onMount } from 'svelte'

	import { asDropZone, asDroppable } from 'svelte-drag-and-drop-actions'
	import { explorerItems, filesCache, isMultipleSelected, selected } from '../store'
	import type { ExplorerItem } from '../types'

	import { format } from 'date-fns'
	import { E } from '../event'
	import { appendPath, formatBytes, outsideClick, py } from '../utils'
	import IconV2 from './ui/IconV2.svelte'

	export let file: ExplorerItem
	let size = file.size ?? '0 B'
	let itemNode: HTMLButtonElement
	let inputEditNode: HTMLInputElement
	let isInside = false

	/**
	 * The ondragleave event was being called even before the mouse left the element,
	 * n serves to condition the ondragleave to be called only when leaving the element
	 **/
	let n = 0

	$: if (size) {
		file.size = size

		updateFileCacheSize(size)

		// Update selected file, useful to get updated file size on properties
		if ($selected.length === 1 && $selected[0].path === file.path) {
			selected.set([file])
		}
	}

	function updateFileCacheSize(size: number) {
		if ($filesCache[file.path]) {
			$filesCache[file.path].file.size = size
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
				await py.createFile(path)
			} else if (file.action === 'createFolder') {
				await py.createFolder(path)
			} else if (file.action === 'rename') {
				await py.rename(file.path, path)
			}

			await E.reload()
		}
	}

	onMount(async () => {
		outsideClick(itemNode, () => {
			file.isEditMode = false
		})

		const cache = $filesCache[file.path]

		if (cache) {
			file = cache.file
		} else {
			filesCache.set({
				...$filesCache,
				...{
					[file.path]: {
						file,
						end: false,
					},
				},
			})

			await py.startFolderSize(file.path)
		}

        // $filesCache[file.path] can be undefined, but it's ok :)
		if (!$filesCache[file.path]?.end) {
			// Calculate size
			while (true) {
				const r = await py.streamFolderSize(file.path)

				// For some reason, some files don't start to calculate size
				// even though I called startFolderSize
				if (!r) {
					await py.startFolderSize(file.path)
					continue
				}

				const { size: newSize, end } = r

				size = newSize
                
				if (end) {
                    if ($filesCache[file.path]) {
                        $filesCache[file.path].end = true
					}
                    
                    console.log('break')
					break
				}
			}
		}
	})

	// Autofocus input edit when appear
	$: if (file.isEditMode && inputEditNode) {
		inputEditNode.focus()
	}
</script>

<button
	class={`item flex items-center w-full hover:bg-[#7f8388]/20 hover:font-bold cursor-pointer outline-none ${
		isInside || $selected.find(item => item.path === file.path)
			? 'bg-purple-300/20 font-bold'
			: ''
	}`}
	data-test-id="explorer-item"
	bind:this={itemNode}
	on:click={() => {
		// if isMultipleSelected, add else set
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
				const folder = file.path

				// @ts-ignore
				await py.rename(path, `${folder}/${name}`)

				await E.reload()

				await E.footerText({
					text: `Moved '${name}' to '${folder}'`,
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
				<IconV2 icon={file.type} />
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
		{format(new Date(file.modified), 'dd/MM/yyyy HH:mm')}
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
