<script lang="ts">
	import { py } from '../utils'
	import Close from './icons/Close.svelte'
	import Maximize from './icons/Maximize.svelte'
	import Minimize from './icons/Minimize.svelte'
</script>

<div class="flex justify-end" id="window-buttons">
	<button
		type="button"
		class="px-4 py-2 hover:bg-zinc-700"
		aria-label="Minimize window"
		on:click={py.minimize}
	>
		<Minimize class="fill-primary" />
	</button>
	<button
		type="button"
		class="px-4 py-2 hover:bg-zinc-700"
		aria-label="Maximize window"
		on:click={py.maximize}
	>
		<Maximize class="fill-primary" />
	</button>
	<button
		type="button"
		class="px-4 py-2 hover:bg-red-500"
		aria-label="Close window"
		on:click={py.close}
	>
		<Close class="fill-primary" />
	</button>
</div>
