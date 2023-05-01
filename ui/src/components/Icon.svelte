<script lang="ts">
	import type { ExplorerItem } from '../types'

	import Folder from './icons/Folder.svelte'
	import Abc from './icons/contextmenu/Abc.svelte'
	import Calendar from './icons/contextmenu/Calendar.svelte'
	import NewFile from './icons/contextmenu/NewFile.svelte'
	import NewFolder from './icons/contextmenu/NewFolder.svelte'
	import Pin from './icons/contextmenu/Pin.svelte'
	import Plus from './icons/contextmenu/Plus.svelte'
	import Size from './icons/contextmenu/Size.svelte'
	import Sort from './icons/contextmenu/Sort.svelte'
	import Types from './icons/contextmenu/Types.svelte'
	import FileAstro from './icons/files/FileAstro.svelte'
	import FileAstroConfig from './icons/files/FileAstroConfig.svelte'
	import FileBinary from './icons/files/FileBinary.svelte'
	import FileCSS from './icons/files/FileCSS.svelte'
	import FileConfig from './icons/files/FileConfig.svelte'
	import FileDatabase from './icons/files/FileDatabase.svelte'
	import FileDefault from './icons/files/FileDefault.svelte'
	import FileDocker from './icons/files/FileDocker.svelte'
	import FileEsLint from './icons/files/FileESLint.svelte'
	import FileFont from './icons/files/FileFont.svelte'
	import FileGit from './icons/files/FileGit.svelte'
	import FileHTML from './icons/files/FileHTML.svelte'
	import FileImage from './icons/files/FileImage.svelte'
	import FileJavascript from './icons/files/FileJavascript.svelte'
	import FileJson from './icons/files/FileJson.svelte'
	import FileLicense from './icons/files/FileLicense.svelte'
	import FileMarkdown from './icons/files/FileMarkdown.svelte'
	import FileNpm from './icons/files/FileNPM.svelte'
	import FilePdf from './icons/files/FilePDF.svelte'
	import FilePnpm from './icons/files/FilePNPM.svelte'
	import FilePostCssConfig from './icons/files/FilePostCSSConfig.svelte'
	import FilePrettier from './icons/files/FilePrettier.svelte'
	import FilePython from './icons/files/FilePython.svelte'
	import FileRst from './icons/files/FileRst.svelte'
	import FileSVG from './icons/files/FileSVG.svelte'
	import FileTsConfig from './icons/files/FileTSConfig.svelte'
	import FileTailwind from './icons/files/FileTailwind.svelte'
	import FileText from './icons/files/FileText.svelte'
	import FileToml from './icons/files/FileToml.svelte'
	import FileTypescript from './icons/files/FileTypescript.svelte'
	import FileTypescriptDef from './icons/files/FileTypescriptDef.svelte'
	import FileYaml from './icons/files/FileYaml.svelte'
	import FileYarn from './icons/files/FileYarn.svelte'
	import FileZip from './icons/files/FileZip.svelte'
	import FolderAssets from './icons/folders/FolderAssets.svelte'
	import FolderCli from './icons/folders/FolderCli.svelte'
	import FolderComponent from './icons/folders/FolderComponent.svelte'
	import FolderDist from './icons/folders/FolderDist.svelte'
	import FolderDocs from './icons/folders/FolderDocs.svelte'
	import FolderGit from './icons/folders/FolderGit.svelte'
	import FolderGithub from './icons/folders/FolderGithub.svelte'
	import FolderNext from './icons/folders/FolderNext.svelte'
	import FolderNodeModules from './icons/folders/FolderNodeModules.svelte'
	import FolderPublic from './icons/folders/FolderPublic.svelte'
	import FolderSrc from './icons/folders/FolderSrc.svelte'
	import FolderTest from './icons/folders/FolderTest.svelte'
	import FolderView from './icons/folders/FolderView.svelte'
	import FolderVscode from './icons/folders/FolderVscode.svelte'

	export let icon: ExplorerItem | string
	export let type: 'file' | 'folder' | 'contextmenu' | '' = ''

	// prettier-ignore
	const fileIcon = {
        'icon'                 : FileDefault,
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
        'Config'               : FileConfig,
        'Yarn'                 : FileYarn,
        'PNPM'                 : FilePnpm,
        'Binary'               : FileBinary,
        'PDF'                  : FilePdf,
        'Docker'               : FileDocker,
        'License'              : FileLicense,
        'Rst'                  : FileRst,
        'Image'                : FileImage,
        'ESLint'               : FileEsLint,
        'NPM'                  : FileNpm,
        'PostCSSConfig'        : FilePostCssConfig,
        'Zip'                  : FileZip,
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
        'CLI'         : FolderCli,
        'Github'      : FolderGithub,
        'Test'        : FolderTest,
        'Docs'        : FolderDocs,
        'Next'        : FolderNext,
    } as Record<string, any>

	// prettier-ignore
	const contextmenuIcon = {
        'NewFile'   : NewFile,
        'Sort'      : Sort,
        'Plus'      : Plus,
        'NewFolder' : NewFolder,
        'Abc'       : Abc,
        'Calendar'  : Calendar,
        'Size'      : Size,
        'Types'     : Types,
        'Pin'       : Pin
    } as Record<string, any>

	function getFileIcon(
		icon: ExplorerItem | string,
		type?: 'file' | 'folder' | 'contextmenu' | '',
	) {
		if (typeof icon === 'string' && type) {
			if (type === 'folder') {
				return folderIcon[icon] || Folder
			} else if (type === 'file') {
				return fileIcon[icon] || FileDefault
			}
			return contextmenuIcon[icon]
		} else if (typeof icon === 'object') {
			if (icon.kind === 'folder') {
				return folderIcon[icon.type] || Folder
			}
			return fileIcon[icon.type] || FileDefault
		}
	}
</script>

<svelte:component this={getFileIcon(icon, type)} />
