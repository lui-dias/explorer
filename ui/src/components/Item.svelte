<script lang="ts">
	import { onMount } from 'svelte'

	import { cwd, footerText, history, historyIndex, refreshExplorer, selectedItem } from '../store'
	import type { ExplorerItem } from '../types'

	import { events } from '../event'
	import { __pywebview, formatBytes, isPathChild, outsideClick } from '../utils'
	import Folder from './icons/Folder.svelte'
	import FileAstro from './icons/files/FileAstro.svelte'
	import FileAstroConfig from './icons/files/FileAstroConfig.svelte'
	import FileCSS from './icons/files/FileCSS.svelte'
	import FileDatabase from './icons/files/FileDatabase.svelte'
	import FileDefault from './icons/files/FileDefault.svelte'
	import FileFont from './icons/files/FileFont.svelte'
	import FileGit from './icons/files/FileGit.svelte'
	import FileHTML from './icons/files/FileHTML.svelte'
	import FileJavascript from './icons/files/FileJavascript.svelte'
	import FileJson from './icons/files/FileJson.svelte'
	import FileMarkdown from './icons/files/FileMarkdown.svelte'
	import FilePrettier from './icons/files/FilePrettier.svelte'
	import FilePython from './icons/files/FilePython.svelte'
	import FileSVG from './icons/files/FileSVG.svelte'
	import FileTsConfig from './icons/files/FileTSConfig.svelte'
	import FileTailwind from './icons/files/FileTailwind.svelte'
	import FileToml from './icons/files/FileToml.svelte'
	import FileTypescript from './icons/files/FileTypescript.svelte'
	import FileTypescriptDef from './icons/files/FileTypescriptDef.svelte'
	import FileYaml from './icons/files/FileYaml.svelte'
	import FolderAssets from './icons/folders/FolderAssets.svelte'
	import FolderComponent from './icons/folders/FolderComponent.svelte'
	import FolderDist from './icons/folders/FolderDist.svelte'
	import FolderNodeModules from './icons/folders/FolderNodeModules.svelte'
	import FolderPublic from './icons/folders/FolderPublic.svelte'
	import FolderSrc from './icons/folders/FolderSrc.svelte'
	import FolderView from './icons/folders/FolderView.svelte'
	import FolderVscode from './icons/folders/FolderVscode.svelte'
	import FileText from './icons/files/FileText.svelte'
	import FolderGit from './icons/folders/FolderGit.svelte'

	export let file: ExplorerItem
	let size = file.size ?? '0 B'
	let itemNode: HTMLButtonElement
	let inputEditNode: HTMLInputElement

	$: if (size) {
		file.size = size
	}

	// prettier-ignore
	const fileIcon = {
        'file'                 : FileDefault,
        'Python'               : FilePython,
        'Prettier'             : FilePrettier,
        'Javascript'           : FileJavascript,
        'Json'                 : FileJson,
        'Tsconfig'             : FileTsConfig,
        'Git'                  : FileGit,
        'Yaml'                 : FileYaml,
        'Markdown'             : FileMarkdown,
        'Toml'                 : FileToml,
        'Astro'                : FileAstro,
        'Astro Config'         : FileAstroConfig,
        'Tailwind'             : FileTailwind,
        'Typescript'           : FileTypescript,
        'Typescript Definition': FileTypescriptDef,
        'Database'             : FileDatabase,
        'SVG'                  : FileSVG,
        'HTML'                 : FileHTML,
        'CSS'                  : FileCSS,
        'Font'                 : FileFont,
        'Text'                 : FileText,
	} as Record<string, any>

	// prettier-ignore
	const folderIcon = {
        'Folder'      : Folder,
        'Vscode'      : FolderVscode,
        'Node Modules': FolderNodeModules,
        'Public'      : FolderPublic,
        'Src'         : FolderSrc,
        'Component'   : FolderComponent,
        'View'        : FolderView,
        'Dist'        : FolderDist,
        'Assets'      : FolderAssets,
        'Git'         : FolderGit,
    } as Record<string, any>

	function getFileIcon(file: ExplorerItem) {
		if (file.kind === 'folder') {
			return folderIcon[file.type] || Folder
		}

		return fileIcon[file.type] || FileDefault
	}

	async function executeEdit() {
		const path = `${file.parent}/${file.name}`

		if (file.action === 'create_file') {
			events.emit('create_file', path)
		} else if (file.action === 'create_folder') {
			events.emit('create_folder', path)
		} else if (file.action === 'rename') {
			const exists = await __pywebview.exists(path, file.path)

			if (file.name === '') {
				footerText.set('The name cannot be empty')
			} else if (exists) {
				footerText.set('The name already exists')
			} else {
				events.emit('rename', file.path, path)
			}
		}

		events.emit('full_reload')
	}

	onMount(async () => {
		outsideClick(itemNode, () => {
			selectedItem.set(null)
		})

		let interval = setInterval(async () => {
			const { size: newSize, end } = await __pywebview.stream_folder_size(file.path)

			size = newSize

			if (end) {
				clearInterval(interval)
			}
		}, 100)

		await __pywebview.reset_stream_size(file.path)
	})

	$: if (file.isEditMode && inputEditNode) {
		inputEditNode.focus()
	}
</script>

<button
	class={`flex w-full dark:hover:bg-purple-300/20 cursor-pointer outline-none ${
		$selectedItem?.path === file.path ? 'bg-purple-300/20' : ''
	}`}
	bind:this={itemNode}
	on:click={() => {
		selectedItem.set(file)
	}}
	on:dblclick={() => {
		if (file.kind === 'folder') {
			cwd.set(file.path)

			history.set([...$history, file.path])

			let index = $history.length - 1

			while (!isPathChild($history[index], file.path)) {
				index--
			}

			history.set($history.slice(0, index + 1))
			history.set([...$history, file.path])
			historyIndex.set(index + 1)
		}
	}}
>
	<div class="w-[50%]">
		{#if file.isEditMode}
			<input
				type="text"
				class="dark:text-purple-100 dark:bg-transparent text-gray-900 outline-none rounded-md px-2 h-full w-full"
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
			<div class="dark:text-purple-100 flex items-center gap-x-1.5 w-64 text-sm">
				<svelte:component this={getFileIcon(file)} />
				<span class="overflow-hidden text-ellipsis whitespace-nowrap w-full text-start">
					{file.name}
				</span>
			</div>
		{/if}
	</div>

	<span class="dark:text-purple-100 text-sm text-start w-[20%]">
		{file.modified}
	</span>
	<span class="dark:text-purple-100 text-sm capitalize text-start w-[15%]">
		{#if file.kind === 'folder'}
			Folder
		{:else}
			{file.kind}
		{/if}
	</span>
	<span class="dark:text-purple-100 text-sm text-right w-[15%]">
		{formatBytes(size)}
	</span>
</button>
