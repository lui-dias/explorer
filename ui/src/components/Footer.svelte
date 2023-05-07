<script lang="ts">
	import { footer, settingsOpen } from '../store'
	import Config from './icons/Config.svelte'
	import Error from './icons/Error.svelte'
	import Info from './icons/Info.svelte'
	import Warning from './icons/Warning.svelte'
</script>

<footer class="flex items-center justify-between h-10 px-2 text-text" id="footer">
	<div class="flex items-center gap-x-2">
		{#if $footer.type !== 'none'}
			{#if $footer.type === 'info'}
				<Info class="fill-primary" />
			{/if}
			{#if $footer.type === 'warning'}
				<Warning class="fill-primary" />
			{/if}
			{#if $footer.type === 'error'}
				<Error class="fill-primary" />
			{/if}
		{/if}

		{$footer.text}
	</div>

	<div class="flex items-center gap-x-2">
		<button
			type="button"
			class="disabled:cursor-not-allowed"
			disabled
			on:click={() => settingsOpen.set(true)}
		>
			<Config class="fill-zinc-500" />
		</button>
	</div>
</footer>
