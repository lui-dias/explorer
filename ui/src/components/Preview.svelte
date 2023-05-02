<script lang="ts">
	import { selected } from '../store'
	import type { ExplorerItem } from '../types'
	import { __pywebview, b64ToUint8Array } from '../utils'
	import Highlight from 'svelte-highlight'
	import python from 'svelte-highlight/languages/python'
	import githubDark from 'svelte-highlight/styles/github-dark'
	import isSvg from 'is-svg'
	import {} from 'highlight.js'

	let selectedItem: ExplorerItem
	let lastSelected: ExplorerItem
	let extension: string
	let data: any
	let isLoading = false

	let imageSignatures = {
		'image/png': [new Uint8Array([0x89, 0x50, 0x4e, 0x47]), 4],
		'image/jpeg': [new Uint8Array([0xff, 0xd8, 0xff, 0xe0]), 4],
		pdf: [new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2d]), 5],
	}

	let type = {} as {
		type: 'image' | 'pdf' | 'svg' | 'text' | 'unknown'
		[key: string]: any
	}

	async function getData() {
		isLoading = true
		data = await __pywebview.read(selectedItem.path)

		const chunk = b64ToUint8Array(data)
		let mime = ''
		let text = ''

		function getText() {
			return (text = atob(data))
		}

		Object.entries(imageSignatures).forEach(([key, value]) => {
			const [signature, length] = value as [Uint8Array, number]

			if (chunk.subarray(0, length).every((v, i) => v === signature[i])) {
				mime = key
			}
		})

		if (mime?.startsWith('image')) {
			type = {
				type: 'image',
				mime,
			}
		} else if (mime === 'pdf') {
			type = {
				type: 'pdf',
			}
		} else if (isSvg(getText())) {
			type = {
				type: 'svg',
			}
		} else if (['py'].some(v => selectedItem.path.endsWith(v))) {
			type = {
				type: 'text',
				text: getText(),
				language: 'python',
			}
		} else {
			type = {
				type: 'unknown',
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

<div class="_preview w-full max-w-[250px] h-full pl-4 overflow-y-auto">
	{#if $selected.length}
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
		{:else if type.type === 'text'}
			{#if type.language === 'python'}
				<Highlight
					language={python}
					code={type.text}
					class="pr-2 overflow-y-auto h-[398px] scrollbar-thin scrollbar-thumb-zinc-700"
				/>
			{/if}
		{/if}
	{/if}
</div>
