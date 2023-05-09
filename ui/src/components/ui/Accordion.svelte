<script lang="ts">
	export let open = false
</script>

<div class={$$props.class}>
	<button type="button" on:click={() => (open = !open)}>
		<slot name="trigger" {open} />
	</button>

	<div
		class="transition-all duration-300 ease-out grid grid-rows-[0fr]"
		class:grid-rows-[1fr]={open}
	>
		<div class="overflow-hidden">
			<slot name="content" {open} />
		</div>
	</div>
</div>
