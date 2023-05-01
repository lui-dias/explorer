<script lang="ts">
	import { selected } from '../store'
	import type { ExplorerItem } from '../types'
	import { __pywebview, b64ToUint8Array } from '../utils'
	import Loading from './Loading.svelte'

	let selectedItem: ExplorerItem
	let lastSelected: ExplorerItem
	let extension: string
	let data: any
	let isLoading = false

	let imageSignatures = {
		'image/png': [new Uint8Array([0x89, 0x50, 0x4e, 0x47]), 4],
		'image/jpeg': [new Uint8Array([0xff, 0xd8, 0xff, 0xe0]), 4],
	}

	let type = {} as {
		type: 'image' | 'unknown'
		[key: string]: any
	}

	async function getData() {
		isLoading = true
		data = await __pywebview.read(selectedItem.path)

		const chunk = b64ToUint8Array(data)
		let mime

		Object.entries(imageSignatures).forEach(([key, value]) => {
			const [signature, length] = value as [Uint8Array, number]

			if (chunk.subarray(0, length).every((v, i) => v === signature[i])) {
				mime = key
			}
		})

		if (mime) {
			type = {
				type: 'image',
				mime,
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

<div class="w-full max-w-[250px] h-full pl-4">
	{#if $selected.length}
		{#if isLoading}
			<span></span>
        {:else}
			{#if type.type === 'image'}
				<img src={`data:${type.mime};base64,${data}`} alt="Preview" />
			{/if}
		{/if}
	{/if}
</div>
