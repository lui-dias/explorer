<script lang="ts">
	import { E } from '../event'
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

	let indexBtn: (i: number) => number
	let indexBtn2: (i: number) => number

	let isHover: boolean | undefined = undefined
	let canBeInvisible = true
	let canBeInvisibleTimer: NodeJS.Timeout

	async function _() {
		if (isHover) {
			canBeInvisible = false

			if (canBeInvisibleTimer) {
				clearTimeout(canBeInvisibleTimer)
			}
		} else {
			canBeInvisibleTimer = setTimeout(() => {
				canBeInvisible = true
			}, 1000)
		}

		await sleep(0.24)
		n = (n + 1) % 2
	}

	$: if (isHover !== undefined) {
		indexBtn(isHover ? 1 : 0)
		indexBtn2(isHover ? 1 : 0)
		_()
	}
</script>

<div class="relative flex flex-col" on:mouseleave={() => (isHover = false)}>
	<div class="z-20" on:mouseenter={() => (isHover = true)}>
		<Button>
			<Icon icon="OtherPlus" slot="icon" colored glow />
		</Button>
	</div>

	<div
		class="absolute top-[calc(100%-8px)] flex flex-col gap-y-2 z-10 pt-4"
		class:invisible={canBeInvisible}
	>
		<Animate {animate} transition={{ ease: 'linear' }} let:motion bind:setIndex={indexBtn}>
			<div use:motion>
				<Button on:click={E.createNewExplorerFile} shadow={n === 1} data-test-id="new-file">
					<Icon icon="OtherNewFile" slot="icon" colored glow />
				</Button>
			</div>
		</Animate>
		<Animate
			animate={animate2}
			let:motion
			transition={{ delay: 0.08, ease: 'linear' }}
			bind:setIndex={indexBtn2}
		>
			<div use:motion>
				<Button
					on:click={E.createNewExplorerFolder}
					shadow={n === 1}
					data-test-id="new-folder"
				>
					<Icon icon="OtherNewFolder" slot="icon" colored glow />
				</Button>
			</div>
		</Animate>
	</div>
</div>
