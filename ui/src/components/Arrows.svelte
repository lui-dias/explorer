<script lang="ts">
	import { E } from '../event'
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
	<Button disabled={backDisabled} class="group" on:click={E.back}>
		<Icon icon="OtherArrowLeft" slot="icon" class="rotate-180" />
	</Button>

	<Button disabled={forwardDisabled} class="group" on:click={E.forward}>
		<Icon icon="OtherArrowLeft" slot="icon" />
	</Button>
</div>
