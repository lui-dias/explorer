<script lang="ts">
	import { events } from '../event'
	import { historyIndex, history } from '../store'
	import ArrowLeft from './icons/ArrowLeft.svelte'

	export let back: () => void
	// prettier-ignore
	export let forward: () => void;

	let backDisabled = $historyIndex === 0
	let forwardDisabled = $historyIndex === $history.length - 1

	$: {
		backDisabled = $historyIndex === 0
		forwardDisabled = $historyIndex === $history.length - 1
	}
</script>

<div class="flex gap-x-2 mx-3">
	<div class="flex gap-x-5">
		<button
			type="button"
			class="neuBtn w-11 h-11 rounded-full flex justify-center items-center group"
			disabled={backDisabled}
			on:click={() => {
				back()
				events.emit('backClick')
			}}
		>
			<ArrowLeft
				class={`${
					backDisabled ? '' : 'glow'
				} unsetFilterClick fill-primary group-disabled:fill-gray-400 transform rotate-180`}
			/>
		</button>

		<button
			type="button"
			class="w-11 h-11 group neuBtn rounded-full flex justify-center items-center"
			disabled={$historyIndex === $history.length - 1}
			on:click={() => {
				forward()
				events.emit('forwardClick')
			}}
		>
			<ArrowLeft
				class={`${forwardDisabled ? '' : 'glow'} fill-primary group-disabled:fill-gray-400`}
			/>
		</button>
	</div>
</div>
