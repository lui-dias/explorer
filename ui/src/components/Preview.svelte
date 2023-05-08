<script lang="ts">
	import isSvg from 'is-svg'
	import Highlight from 'svelte-highlight'
	import {
		css,
		javascript,
		json,
		markdown,
		plaintext,
		powershell,
		python,
		ini as tomlAndIni,
		typescript,
		vbscriptHtml,
		yaml,
	} from 'svelte-highlight/languages'
	import githubDark from 'svelte-highlight/styles/github-dark'
	import { selected } from '../store'
	import type { ExplorerItem } from '../types'

	let selectedItem: ExplorerItem
	let lastSelected: ExplorerItem
	let extension: string
	let data: any
	let isLoading = false

	let type = {} as {
		type: 'image' | 'pdf' | 'svg' | 'text' | 'video' | 'unknown'
		[key: string]: any
	}

	let languages = new Map<any, string[]>([
		[python, ['.py']],
		[tomlAndIni, ['.toml', '.ini']],
		[plaintext, ['.txt']],
		[markdown, ['.md']],
		[json, ['.json', '.prettierrc']],
		[javascript, ['.js', '.mjs', '.cjs']],
		[yaml, ['.yml', '.yaml']],
		[typescript, ['.ts', '.tsx']],
		[vbscriptHtml, ['.html']],
		[css, ['.css']],
		[powershell, ['.ps1']],
	])

	let images = ['png', 'jpg', 'jpeg']

	async function getData() {
		isLoading = true

		let text = ''
		let language = ''

		function getText() {
			return (text = atob(data))
		}

		for (const [key, value] of languages) {
			if (value.some(v => selectedItem.name.endsWith(v))) {
				language = key
			}
		}

		if (images.includes(extension)) {
			type = {
				type: 'image',
				mime: extension,
			}
		} else if (extension === 'pdf') {
			type = {
				type: 'pdf',
			}
		} else if (
			[
				'3g2',
				'3gp',
				'asf',
				'amv',
				'avi',
				'divx',
				'qt',
				'f4a',
				'f4b',
				'f4p',
				'f4v',
				'flv',
				'm2v',
				'm4v',
				'mkv',
				'mk3d',
				'mov',
				'mp2',
				'mp4',
				'mpe',
				'mpeg',
				'mpeg2',
				'mpg',
				'mpv',
				'nsv',
				'ogv',
				'rm',
				'rmvb',
				'svi',
				'vob',
				'webm',
				'wmv',
			].includes(extension)
		) {
			type = {
				type: 'video',
			}
		} else if (isSvg(getText())) {
			type = {
				type: 'svg',
			}
		} else {
			type = {
				type: 'text',
				text: getText(),
				language: language || plaintext,
			}
		}

		type = { ...type }

		isLoading = false
	}

	$: {
		if ($selected.length > 0) {
			selectedItem = $selected[0]
			extension = selectedItem.name.split('.').pop()!

			if (selectedItem.path !== lastSelected?.path) {
				lastSelected = selectedItem
				getData()
			}
		}
	}
</script>

<svelte:head>
	{@html githubDark}
</svelte:head>

<div
	class={`_preview w-full transition-all duration-300 ease-out h-[398px] pl-4 overflow-y-auto ${
		$selected.length === 1 && $selected[0].kind === 'file' ? 'max-w-[250px]' : 'max-w-0'
	}`}
>
	{#if $selected.length === 1 && $selected[0].kind === 'file'}
		{#if isLoading}
			<span />
		{:else if type.type === 'image'}
			<img src={`data:${type.mime};base64,${data}`} alt="Preview" />
		{:else if type.type === 'pdf'}
			<span />
		{:else if type.type === 'svg'}
			<div class="flex items-center justify-center w-full h-full bg-zinc-200/20">
				<img src={`data:image/svg+xml;base64,${data}`} alt="Preview" />
			</div>
		{:else if type.type === 'video'}
			<!-- svelte-ignore a11y-media-has-caption -->
			<video src={`http://localhost:3003/stream/${selectedItem.path}`} controls autoplay />
		{:else if type.type === 'text'}
			<Highlight
				language={type.language}
				code={type.text}
				class="pr-2 overflow-auto h-full scrollbar-thin scrollbar-thumb-zinc-700 [&>*]:scrollbar-thin [&>*]:scrollbar-thumb-zinc-700 [&>*]:h-full"
			/>
		{/if}
	{/if}
</div>
