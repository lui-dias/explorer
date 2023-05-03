<script lang="ts">
	import { explorerItems, cwd, scrollExplorerToEnd, contextMenuOpen } from '../store'
	import { formatDate } from '../utils'
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
			<button
				type="button"
				use:motion
				on:click={() => {
					contextMenuOpen.set(false)

					explorerItems.set([
						...$explorerItems,
						{
							name: 'file',
							path: $cwd + '/file',
							isEditMode: true,
							kind: 'file',
							size: 0,
							parent: $cwd,
							modified: formatDate(new Date()),
							type: 'Text',
							action: 'create_file',
						},
					])

					$scrollExplorerToEnd()
				}}
			>
				<Button>
					<NewFile slot="icon" />
				</Button>
			</button>
		</Animate>
		<Animate
			animate={animate2}
			let:motion
			bind:cycle={cycleBtn2}
			transition={{ delay: 0.1, ease: 'linear' }}
		>
			<button
				type="button"
				use:motion
				on:click={() => {
					contextMenuOpen.set(false)

					explorerItems.set([
						...$explorerItems,
						{
							name: 'folder',
							path: $cwd + '/folder',
							isEditMode: true,
							kind: 'folder',
							size: 0,
							parent: $cwd,
							modified: formatDate(new Date()),
							type: 'Folder',
							action: 'create_folder',
						},
					])

					$scrollExplorerToEnd()
				}}
			>
				<Button>
					<NewFolder slot="icon" />
				</Button>
			</button>
		</Animate>
	</div>
</div>
