<script lang="ts">
	import { historyIndex, history } from '../store'
	import ArrowLeft from './icons/ArrowLeft.svelte'

	export let back: () => void
	export let forward: () => void
</script>

<div class="flex gap-x-2 mx-3">
	<div class="flex gap-x-3">
		<button type="button" class="w-3" disabled={$historyIndex === 0} on:click={back}>
			<ArrowLeft class="fill-primary" />
		</button>

		<button
			type="button"
			class="transform rotate-180 w-3"
			disabled={$historyIndex === $history.length - 1}
			on:click={forward}
		>
			<ArrowLeft class="fill-primary" />
		</button>
	</div>
</div>
