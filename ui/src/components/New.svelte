<script lang="ts">
	import { events } from '../event'
	import Animate from './Animate.svelte'
	import NewFile from './icons/NewFile.svelte'
	import NewFolder from './icons/NewFolder.svelte'
	import Plus from './icons/Plus.svelte'
	import Button from './ui/Button.svelte'

	const animate = {
		y: [-55, 0],
	}
	const animate2 = {
		y: [-105, 0],
	}

	let cycleBtn: () => number
	let cycleBtn2: () => number

	let isHover: boolean | undefined = undefined

	$: if (isHover !== undefined && cycleBtn && cycleBtn2) {
		cycleBtn()
		cycleBtn2()
	}
</script>

<div
	class="relative flex flex-col"
	on:mouseenter={() => (isHover = true)}
	on:mouseleave={() => (isHover = false)}
>
	<button type="button" class="z-20">
		<Button>
			<Plus slot="icon" />
		</Button>
	</button>

	<div class="absolute top-[calc(100%-8px)] flex flex-col gap-y-2 z-10 pt-4">
		<Animate {animate} transition={{ ease: 'linear' }} let:motion bind:cycle={cycleBtn}>
			<div use:motion>
				<Button on:click={() => events.emit('createNewFile')}>
					<NewFile slot="icon" />
				</Button>
			</div>
		</Animate>
		<Animate
			animate={animate2}
			let:motion
			bind:cycle={cycleBtn2}
			transition={{ delay: 0.08, ease: 'linear' }}
		>
			<div use:motion>
				<Button on:click={() => events.emit('createNewFolder')}>
					<NewFolder slot="icon" />
				</Button>
			</div>
		</Animate>
	</div>
</div>
