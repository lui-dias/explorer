<script lang="ts">
	import { createEventDispatcher } from 'svelte'
	import type { HTMLButtonAttributes } from 'svelte/elements'
	import { tv } from 'tailwind-variants'

	const button = tv({
		slots: {
			border: 'p-0.5 bg-[linear-gradient(145deg,#4f5559,#131517)] rounded-full shadow-[6px_6px_15px_#24282a,_-6px_-6px_15px_#3d4347]',
			inner: 'flex items-center justify-center w-11 h-11 rounded-full bg-[linear-gradient(145deg,#2d3134,#3f454a)]',
		},
	})

	const onClick = createEventDispatcher()

	const { border, inner } = button()

	// prettier-ignore
	type $$Props = HTMLButtonAttributes;
</script>

<button
	type="button"
	{...$$restProps}
	class={`${border()} ${$$props.class}`}
	on:click={e => onClick('click', e)}
>
	<div class={inner()}>
		<slot name="icon" />
	</div>
</button>
