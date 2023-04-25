<script lang="ts">
	import { __pywebview } from '../utils'
	import Close from './icons/Close.svelte'
	import Maximize from './icons/Maximize.svelte'
	import Minimize from './icons/Minimize.svelte'
</script>

<div class="flex justify-end">
	<button type="button" class="hover:bg-zinc-700 py-2 px-4" on:click={__pywebview.minimize}>
		<Minimize class="fill-primary" />
	</button>
	<button type="button" class="hover:bg-zinc-700 py-2 px-4" on:click={__pywebview.maximize}>
		<Maximize class="fill-primary" />
	</button>
	<button type="button" class="hover:bg-red-500 py-2 px-4" on:click={__pywebview.close}>
		<Close class="fill-primary" />
	</button>
</div>
