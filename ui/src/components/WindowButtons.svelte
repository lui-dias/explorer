<script lang="ts">
	import { __pywebview } from '../utils'
	import Close from './icons/Close.svelte'
	import Maximize from './icons/Maximize.svelte'
	import Minimize from './icons/Minimize.svelte'
</script>

<div class="flex justify-end" id="window-buttons">
	<button type="button" class="px-4 py-2 hover:bg-zinc-700" on:click={__pywebview.minimize}>
		<Minimize class="fill-primary" />
	</button>
	<button type="button" class="px-4 py-2 hover:bg-zinc-700" on:click={__pywebview.maximize}>
		<Maximize class="fill-primary" />
	</button>
	<button type="button" class="px-4 py-2 hover:bg-red-500" on:click={__pywebview.close}>
		<Close class="fill-primary" />
	</button>
</div>
