<script lang="ts">
	import { events } from '../event'
	import { history, historyIndex } from '../store'
	import Button from './ui/Button.svelte'
	import Icon from './ui/Icon.svelte'

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
		class="group"
		on:click={() => {
			events.emit('back')
			events.emit('clickBack')
		}}
	>
		<Icon icon="OtherArrowLeft" slot="icon" class="rotate-180" />
	</Button>

	<Button
		disabled={forwardDisabled}
		class="group"
		on:click={() => {
			events.emit('forward')
			events.emit('clickForward')
		}}
	>
		<Icon icon="OtherArrowLeft" slot="icon" />
	</Button>
</div>
