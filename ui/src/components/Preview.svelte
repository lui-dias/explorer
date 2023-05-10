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
	import { __pywebview, loadFontDynamicly } from '../utils'

	let selectedItem: ExplorerItem
	let lastSelected: ExplorerItem
	let extension: string
	let data: any
	let isLoading = false
	let weight: number | null
	let font = {
		actual: '',
		loaded: [],
	} as {
		actual: string
		loaded: {
			name: string
			path: string
			weight: number | null
		}[]
	}

	let type = {} as {
		type: 'unknown' | 'image' | 'pdf' | 'svg' | 'text' | 'video' | 'font'
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

		let language = ''

		async function getText() {
			return (data = atob(await __pywebview.read(selectedItem.path)))
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
		} else if (
			['woff', 'woff2', 'ttf', 'otf', 'eot', 'pfa', 'pfb', 'sfd'].includes(extension)
		) {
			type = {
				type: 'font',
			}
		} else if (isSvg(await getText())) {
			type = {
				type: 'svg',
			}
		} else {
			type = {
				type: 'text',
				text: data,
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

	$: if (type.type === 'font') {
		async function _() {
			const fontName = await loadFontDynamicly(
				encodeURI(`http://localhost:3003/stream/${selectedItem.path}`),
			)
			weight = await __pywebview.getFontWeight(selectedItem.path)
			console.log(weight)

			font.actual = fontName
			font.loaded = [
				...font.loaded,
				{
					name: fontName,
					path: selectedItem.path,
					weight,
				},
			]

			font = { ...font }
		}

		if (font.loaded.some(f => f.path === selectedItem.path)) {
			font.actual = font.loaded.find(f => f.path === selectedItem.path)!.name
			font = { ...font }
		} else {
			font.actual = ''
			_()
		}
	}
</script>

<svelte:head>
	{@html githubDark}
</svelte:head>

<div
	class={`_preview w-full transition-all duration-300 ease-out h-[398px] pl-4 overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 ${
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
		{:else if type.type === 'font'}
			<div class="bg-zinc-200/50 p-2 overflow-x-auto scrollbar-thin scrollbar-thumb-zinc-700">
				<div class="">
					{#if weight}
						<p class="text-sm">Weight {weight}</p>
						<p>---------------------------</p>
					{:else if weight === null}
						<p class="text-sm">It was not possible to get the weight of this font</p>
					{/if}
					<div>
						{#each [12, 16, 24, 32, 48, 64] as size}
                            <div class="flex items-center gap-x-2">
                                <p class="text-sm">{size}</p>
                                <p
                                    class="font-thin whitespace-nowrap"
                                    style={`font-family: ${font.actual}; font-weight: ${weight}; font-size: ${size}px`}
                                >
                                    The quick brown fox jumps over the lazy dog
                                </p>
                            </div>
						{/each}
					</div>
				</div>
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
