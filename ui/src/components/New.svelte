<script lang="ts">
	import { events } from '../event'
	import { sleep } from '../utils'
	import Animate from './Animate.svelte'
	import Button from './ui/Button.svelte'
	import Icon from './ui/Icon.svelte'

	const animate = {
		y: [-50, 0],
	}
	const animate2 = {
		y: [-105, 0],
	}

	let n = 0
	let cycleBtn: () => number
	let cycleBtn2: () => number

	let isHover: boolean | undefined = undefined

	async function _() {
		await sleep(0.24)
		n = (n + 1) % 2
	}

	$: if (isHover !== undefined && cycleBtn && cycleBtn2) {
		cycleBtn()
		cycleBtn2()
		_()
	}
</script>

<div class="relative flex flex-col" on:mouseleave={() => (isHover = false)}>
	<div class="z-20" on:mouseenter={() => (isHover = true)}>
		<Button>
			<Icon icon="OtherPlus" slot="icon" />
		</Button>
	</div>

	<div class="absolute top-[calc(100%-8px)] flex flex-col gap-y-2 z-10 pt-4">
		<Animate {animate} transition={{ ease: 'linear' }} let:motion bind:cycle={cycleBtn}>
			<div use:motion>
				<Button on:click={() => events.emit('createNewExplorerFile')} shadow={n === 1}>
					<Icon icon="OtherNewFile" slot="icon" />
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
				<Button on:click={() => events.emit('createNewExplorerFolder')} shadow={n === 1}>
					<Icon icon="OtherNewFolder" slot="icon" />
				</Button>
			</div>
		</Animate>
	</div>
</div>
