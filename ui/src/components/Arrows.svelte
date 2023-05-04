<script lang="ts">
	import { events } from '../event'
	import { history, historyIndex } from '../store'
	import Button from './ui/Button.svelte'
	import Icon from './ui/Icon.svelte'

	export let back: () => void
	export let forward: () => void

	let backDisabled = $historyIndex === 0
	let forwardDisabled = $historyIndex === $history.length - 1

	$: {
		backDisabled = $historyIndex === 0
		forwardDisabled = $historyIndex === $history.length - 1
	}
</script>

<div class="flex gap-x-2">
	<Button
		disabled={backDisabled}
		on:click={() => {
			back()
			events.emit('backClick')
		}}
	>
		<Icon icon="OtherArrowLeft" slot="icon" class="rotate-180" />
	</Button>

	<Button
		disabled={forwardDisabled}
		on:click={() => {
			forward()
			events.emit('forwardClick')
		}}
	>
		<Icon icon="OtherArrowLeft" slot="icon" />
	</Button>
</div>
