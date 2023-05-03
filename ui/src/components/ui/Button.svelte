<script lang="ts">
	import { tv } from 'tailwind-variants'

	const button = tv({
		slots: {
			border: 'bg-[linear-gradient(145deg,#4f5559,#131517)] rounded-full shadow-[6px_6px_15px_#24282a,_-6px_-6px_15px_#3d4347]',
			inner: 'flex items-center justify-center w-11 h-11 rounded-full bg-[linear-gradient(145deg,#2d3134,#3f454a)] group',
			icon: 'glow fill-primary group-disabled:fill-gray-400',
		},
	})

	const { border, inner, icon } = button()
</script>

<div class={border()}>
	<div class={inner()}>
		<span class={icon()}>
			<slot name="icon" />
		</span>
	</div>
</div>
