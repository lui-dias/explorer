<script lang="ts">
	import type { ExplorerItem } from '../types'
	import { formatBytes } from '../utils'
	import Accordion from './ui/Accordion.svelte'
	import Icon from './ui/Icon.svelte'
	import { formatDistance } from 'date-fns'

	export let propertiesNode: HTMLDialogElement | null = null
	export let file: ExplorerItem
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<dialog
	class="w-72 h-[600px] rounded-md bg-gradient-to-b from-[#404449] to-[#2A2D32]"
	bind:this={propertiesNode}
	on:click={() => {
		if (propertiesNode) {
			propertiesNode.close()
		}
	}}
>
	{#if file}
		<div on:click={e => e.stopPropagation()} class="w-full h-full">
			<div>
				<div class="flex items-center gap-x-2">
					<Icon icon={file.type} />
					<strong class="text-[#ececec] text-lg">
						{file.name}
					</strong>
				</div>
				<p class="text-[12px] text-[#7f8388]">
					{file.parent}
				</p>
			</div>

			<Accordion class="w-full [&>*]:w-full mt-8" open>
				<div slot="trigger" class="flex justify-between items-center w-full" let:open>
					<strong class="text-[#ececec] dark:text-text-light tracking-wide font-inter">
						Details
					</strong>
					<Icon
						icon="OtherChevron"
						class={`${
							open ? 'rotate-[270deg]' : 'rotate-180'
						} transition-transform duration-300 fill-[#b9b9b9]`}
					/>
				</div>
				<div slot="content" class="w-full space-y-1 mt-2">
					<div class="w-full flex justify-between">
						<span class="text-[#7f8388] text-sm">Size:</span>
						<strong class="text-[#b9b9b9] text-sm">{formatBytes(file.size)}</strong>
					</div>
					<div class="w-full flex justify-between">
						<span class="text-[#7f8388] text-sm">Created at:</span>
						<strong class="text-[#b9b9b9] text-sm"
							>{formatDistance(new Date(file.created), new Date())}</strong
						>
					</div>
					<div class="w-full flex justify-between">
						<span class="text-[#7f8388] text-sm">Modified at:</span>
						<strong class="text-[#b9b9b9] text-sm"
							>{formatDistance(new Date(file.modified), new Date())}</strong
						>
					</div>
					<div class="w-full flex justify-between">
						<span class="text-[#7f8388] text-sm">Accessed at:</span>
						<strong class="text-[#b9b9b9] text-sm"
							>{formatDistance(new Date(file.accessed), new Date())}</strong
						>
					</div>
				</div>
			</Accordion>
		</div>
	{/if}
</dialog>
