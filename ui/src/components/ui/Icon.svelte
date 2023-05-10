<script lang="ts">
	import ArrowLeft from '../icons/ArrowLeft.svelte'
	import Chevron from '../icons/Chevron.svelte'
	import Disk from '../icons/Disk.svelte'
	import Folder from '../icons/Folder.svelte'
	import Search from '../icons/Search.svelte'
	import Abc from '../icons/contextmenu/Abc.svelte'
	import Asc from '../icons/contextmenu/Asc.svelte'
	import Calendar from '../icons/contextmenu/Calendar.svelte'
	import Desc from '../icons/contextmenu/Desc.svelte'
	import NewFile from '../icons/contextmenu/NewFile.svelte'
	import NewFolder from '../icons/contextmenu/NewFolder.svelte'
	import Pin from '../icons/contextmenu/Pin.svelte'
	import Plus from '../icons/contextmenu/Plus.svelte'
	import Size from '../icons/contextmenu/Size.svelte'
	import Sort from '../icons/contextmenu/Sort.svelte'
	import Types from '../icons/contextmenu/Types.svelte'
	import Unpin from '../icons/contextmenu/Unpin.svelte'
	import FileAstro from '../icons/files/FileAstro.svelte'
	import FileAstroConfig from '../icons/files/FileAstroConfig.svelte'
	import FileBinary from '../icons/files/FileBinary.svelte'
	import FileCSS from '../icons/files/FileCSS.svelte'
	import FileConfig from '../icons/files/FileConfig.svelte'
	import FileDatabase from '../icons/files/FileDatabase.svelte'
	import FileDefault from '../icons/files/FileDefault.svelte'
	import FileDocker from '../icons/files/FileDocker.svelte'
	import FileEsLint from '../icons/files/FileESLint.svelte'
	import FileFont from '../icons/files/FileFont.svelte'
	import FileGit from '../icons/files/FileGit.svelte'
	import FileHTML from '../icons/files/FileHTML.svelte'
	import FileImage from '../icons/files/FileImage.svelte'
	import FileJavascript from '../icons/files/FileJavascript.svelte'
	import FileJson from '../icons/files/FileJson.svelte'
	import FileLicense from '../icons/files/FileLicense.svelte'
	import FileMarkdown from '../icons/files/FileMarkdown.svelte'
	import FileNpm from '../icons/files/FileNPM.svelte'
	import FilePdf from '../icons/files/FilePDF.svelte'
	import FilePnpm from '../icons/files/FilePNPM.svelte'
	import FilePostCssConfig from '../icons/files/FilePostCSSConfig.svelte'
	import FilePrettier from '../icons/files/FilePrettier.svelte'
	import FilePython from '../icons/files/FilePython.svelte'
	import FileRst from '../icons/files/FileRst.svelte'
	import FileSVG from '../icons/files/FileSVG.svelte'
	import FileTsConfig from '../icons/files/FileTSConfig.svelte'
	import FileTailwind from '../icons/files/FileTailwind.svelte'
	import FileText from '../icons/files/FileText.svelte'
	import FileToml from '../icons/files/FileToml.svelte'
	import FileTypescript from '../icons/files/FileTypescript.svelte'
	import FileTypescriptDef from '../icons/files/FileTypescriptDef.svelte'
	import FileVideo from '../icons/files/FileVideo.svelte'
	import FileYaml from '../icons/files/FileYaml.svelte'
	import FileYarn from '../icons/files/FileYarn.svelte'
	import FileZip from '../icons/files/FileZip.svelte'
	import FolderAssets from '../icons/folders/FolderAssets.svelte'
	import FolderCli from '../icons/folders/FolderCli.svelte'
	import FolderComponent from '../icons/folders/FolderComponent.svelte'
	import FolderDist from '../icons/folders/FolderDist.svelte'
	import FolderDocs from '../icons/folders/FolderDocs.svelte'
	import FolderGit from '../icons/folders/FolderGit.svelte'
	import FolderGithub from '../icons/folders/FolderGithub.svelte'
	import FolderNext from '../icons/folders/FolderNext.svelte'
	import FolderNodeModules from '../icons/folders/FolderNodeModules.svelte'
	import FolderPublic from '../icons/folders/FolderPublic.svelte'
	import FolderSrc from '../icons/folders/FolderSrc.svelte'
	import FolderTest from '../icons/folders/FolderTest.svelte'
	import FolderView from '../icons/folders/FolderView.svelte'
	import FolderVscode from '../icons/folders/FolderVscode.svelte'

	import { tv } from 'tailwind-variants'

	const _icon = tv({
		variants: {
			glow: {
				true: 'drop-shadow-[0_0_5px_var(--primary)]',
				false: '',
			},
			colored: {
				true: 'fill-primary group-disabled:fill-gray-400 group-disabled:drop-shadow-none',
				false: '',
			},
		},
	})

	export let glow = false
	export let colored = false
	export let icon: string

	// prettier-ignore
	const icons = {
        'File'                     : FileDefault,
        'FilePython'               : FilePython,
        'FilePrettier'             : FilePrettier,
        'FileJavascript'           : FileJavascript,
        'FileJson'                 : FileJson,
        'FileTsconfig'             : FileTsConfig,
        'FileGit'                  : FileGit,
        'FileYaml'                 : FileYaml,
        'FileMarkdown'             : FileMarkdown,
        'FileToml'                 : FileToml,
        'FileAstro'                : FileAstro,
        'FileAstro Config'         : FileAstroConfig,
        'FileTailwind'             : FileTailwind,
        'FileTypescript'           : FileTypescript,
        'FileTypescript Definition': FileTypescriptDef,
        'FileDatabase'             : FileDatabase,
        'FileSVG'                  : FileSVG,
        'FileHTML'                 : FileHTML,
        'FileCSS'                  : FileCSS,
        'FileFont'                 : FileFont,
        'FileText'                 : FileText,
        'FileConfig'               : FileConfig,
        'FileYarn'                 : FileYarn,
        'FilePNPM'                 : FilePnpm,
        'FileBinary'               : FileBinary,
        'FilePDF'                  : FilePdf,
        'FileDocker'               : FileDocker,
        'FileLicense'              : FileLicense,
        'FileRst'                  : FileRst,
        'FileImage'                : FileImage,
        'FileESLint'               : FileEsLint,
        'FileNPM'                  : FileNpm,
        'FilePostCSSConfig'        : FilePostCssConfig,
        'FileZip'                  : FileZip,
        'FileVideo'                : FileVideo,
        'Folder'                   : Folder,
        'FolderVscode'             : FolderVscode,
        'FolderNode Modules'       : FolderNodeModules,
        'FolderPublic'             : FolderPublic,
        'FolderSrc'                : FolderSrc,
        'FolderComponent'          : FolderComponent,
        'FolderView'               : FolderView,
        'FolderDist'               : FolderDist,
        'FolderAssets'             : FolderAssets,
        'FolderGit'                : FolderGit,
        'FolderCLI'                : FolderCli,
        'FolderGithub'             : FolderGithub,
        'FolderTest'               : FolderTest,
        'FolderDocs'               : FolderDocs,
        'FolderNext'               : FolderNext,
        'OtherNewFile'             : NewFile,
        'OtherArrowLeft'           : ArrowLeft,
        'OtherSort'                : Sort,
        'OtherPlus'                : Plus,
        'OtherNewFolder'           : NewFolder,
        'OtherAbc'                 : Abc,
        'OtherCalendar'            : Calendar,
        'OtherSize'                : Size,
        'OtherTypes'               : Types,
        'OtherPin'                 : Pin,
        'OtherUnpin'               : Unpin,
        'OtherSearch'              : Search,
        'OtherDisk'                : Disk,
        'OtherChevron'             : Chevron,
        'OtherAsc'                 : Asc,
        'OtherDesc'                : Desc
	} as Record<string, any>
</script>

<svelte:component this={icons[icon]} class={`${_icon({ glow, colored })} ${$$props.class}`} />
