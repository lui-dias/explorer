<script lang="ts">
	import { createEventDispatcher } from 'svelte'
	import type { HTMLButtonAttributes } from 'svelte/elements'
	import { tv } from 'tailwind-variants'

	const button = tv({
		slots: {
			inner: 'relative flex items-center justify-center w-11 h-11 rounded-full bg-[linear-gradient(145deg,#2d3134,#3f454a)] enabled:active:bg-[linear-gradient(145deg,#212426,#40464B)]',
			after: 'after:w-[calc(100%+4px)] after:h-[calc(100%+4px)] after:absolute after:-z-10 after:bg-[linear-gradient(145deg,#4f5559,#131517)] after:rounded-full',
		},
		variants: {
			shadow: {
				true: {
					after: 'after:shadow-[6px_6px_15px_#24282a,_-6px_-6px_15px_#3d4347]',
				},
				false: {
					after: '',
				},
			},
		},
	})

	type $$Props = HTMLButtonAttributes & {
		shadow?: boolean
		'data-test-id'?: string
	}

	const onClick = createEventDispatcher()

	let { inner, after } = button({ shadow: $$restProps.shadow ?? true })

	$: {
		const _ = button({ shadow: $$restProps.shadow ?? true })
		inner = _.inner
		after = _.after
	}
</script>

<button
	type="button"
	{...$$restProps}
	class={`${inner()} ${after()} ${$$restProps.class ?? ''}`}
	on:click={e => onClick('click', e)}
>
	<slot name="icon" />
</button>
