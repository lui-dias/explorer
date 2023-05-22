<script lang="ts">
	import { asDropZone } from 'svelte-drag-and-drop-actions'
	import { E } from '../event'
	import { cwd, cwdSplit, history, historyIndex, searchItems } from '../store'
	import { py } from '../utils'
	import Chevron from './icons/Chevron.svelte'

	export let cwdItemIndex: number
	export let dir: string
	export let hideNItems: number

	/**
	 * The ondragleave event was being called even before the mouse left the element,
	 * n serves to condition the ondragleave to be called only when leaving the element
	 **/
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
			// Move file to new folder

			const folder = $cwdSplit.slice(0, cwdItemIndex + 1).join('/')
			const fileToMove = Object.values(data)[0]
			// @ts-ignore
			const name = fileToMove.split('/').pop()

			// @ts-ignore
			await py.rename(fileToMove, `${folder}/${name}`)

			await E.reload()

			await E.footerText({
				text: `Moved '${name}' to '${folder}'`,
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
			// Handle click in cwd item

			const folder = $cwdSplit.slice(0, hideNItems + cwdItemIndex + 1).join('/')
			const isLastItem = cwdItemIndex === $cwdSplit.length - 1 - hideNItems

			await py.deleteAllStreamsFind()
			searchItems.set([])

			if (!isLastItem) {
				// Just add folder to history and update historyIndex and cwd
				history.set([...$history, folder])
				historyIndex.set($history.length)
				cwd.set(folder)
			} else {
				await E.reload()
			}
		}}
	>
		<span class="text-[#b9b9b9] whitespace-nowrap">{dir}</span>
	</button>
	{#if dir !== $cwdSplit.at(-1)}
		<span class="rotate-180">
			<Chevron class="fill-[#b9b9b9] w-5" />
		</span>
	{/if}
</li>
