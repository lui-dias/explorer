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
	<div data-test-id="back">
		<Button
			disabled={backDisabled}
			class="group disabled:cursor-not-allowed"
			aria-label="Back to previous folder of history"
			on:click={E.back}
		>
			<Icon icon="OtherArrowLeft" slot="icon" class="rotate-180" colored glow />
		</Button>
	</div>

	<div data-test-id="forward">
		<Button
			disabled={forwardDisabled}
			class="group disabled:cursor-not-allowed"
			aria-label="Forward to next folder of history"
			on:click={E.forward}
		>
			<Icon icon="OtherArrowLeft" slot="icon" colored glow />
		</Button>
	</div>
</div>
