<script lang="ts">
	import type { ExplorerItem } from '../types'

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
	import FileText from './icons/files/FileText.svelte'
	import FileToml from './icons/files/FileToml.svelte'
	import FileTypescript from './icons/files/FileTypescript.svelte'
	import FileTypescriptDef from './icons/files/FileTypescriptDef.svelte'
	import FileYaml from './icons/files/FileYaml.svelte'
	import FolderAssets from './icons/folders/FolderAssets.svelte'
	import FolderComponent from './icons/folders/FolderComponent.svelte'
	import FolderDist from './icons/folders/FolderDist.svelte'
	import FolderGit from './icons/folders/FolderGit.svelte'
	import FolderNodeModules from './icons/folders/FolderNodeModules.svelte'
	import FolderPublic from './icons/folders/FolderPublic.svelte'
	import FolderSrc from './icons/folders/FolderSrc.svelte'
	import FolderView from './icons/folders/FolderView.svelte'
	import FolderVscode from './icons/folders/FolderVscode.svelte'

	export let file: ExplorerItem

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
</script>

<svelte:component this={getFileIcon(file)} class={$$props.class} />
