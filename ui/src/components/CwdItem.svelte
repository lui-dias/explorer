<script lang="ts">
	import { asDropZone } from 'svelte-drag-and-drop-actions'
	import { cwd, cwdSplit, history, historyIndex, searchItems } from '../store'
	import { py, sleep } from '../utils'
	import Chevron from './icons/Chevron.svelte'
	import { E } from '../event'

	export let i: number
	export let dir: string
	export let hideNItems: number

	let n = 0
	let isInside = false
</script>

<li
	class="flex items-center"
	data-test-id="cwd-item"
	on:dragleave={e => {
		n -= 1

		if (n === 0) {
			isInside = false
		}
	}}
	on:dragenter={e => {
		n += 1
		isInside = true
	}}
	on:drop={e => {
		n -= 1
		isInside = false

		if (n === 0) {
			isInside = false
		}
	}}
	use:asDropZone={{
		TypesToAccept: { 'text/plain': 'copy' },
		// @ts-ignore
		onDrop: async (x, y, Operation, data) => {
			const path = $cwdSplit.slice(0, i + 1).join('/')
			const fileToMove = Object.values(data)[0]
			// @ts-ignore
			const name = fileToMove.split('/').pop()

			// @ts-ignore
			await py.rename(fileToMove, `${path}/${name}`)

			await E.reload()

			await E.footerText({
				text: `Moved '${name}' to '${path}'`,
				type: 'info',
			})
		},
	}}
>
	<button
		type="button"
		class={`dark:hover:bg-[#7f8388]/20 p-2 ${isInside ? 'bg-[#7f8388]/20' : ''}`}
		data-test-id="cwd-item-button"
		on:click={async () => {
			const path = $cwdSplit.slice(0, hideNItems + i + 1).join('/')
			const isLastItem = i === $cwdSplit.length - 1 - hideNItems

			console.log('start')
			await py.delete_all_streams_find()
			searchItems.set([])

			if (!isLastItem) {
				history.set([...$history, path])
				historyIndex.set($history.length)
				cwd.set(path)
			} else {
				await E.reload()
			}
		}}
	>
		<span class="text-[#b9b9b9] whitespace-nowrap">{dir}</span>
	</button>
	{#if dir !== $cwdSplit.slice(-1)[0]}
		<span class="rotate-180">
			<Chevron class="fill-[#b9b9b9] w-5" />
		</span>
	{/if}
</li>
