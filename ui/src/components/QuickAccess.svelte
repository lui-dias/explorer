<script lang="ts">
	import { onMount } from 'svelte'
	import { contextMenuOpen, quickAccess, selectedQuickAccess } from '../store'
	import { appendPath, py } from '../utils'
	import Icon from './ui/Icon.svelte'

	onMount(async () => {
		const items = JSON.parse((await py.get('quickAccess')) ?? '[]') as string[]
		const files = await Promise.all(items.map(async item => await py.get_path_info(item)))

		quickAccess.set(files)
	})
</script>

<ul class="text-sm text-text">
	{#each $quickAccess as file}
		<li
			class={`pl-4 hover:font-bold hover:scale-[115%] transition-transform ${
				$selectedQuickAccess?.path === file.path ? 'font-bold' : ''
			}`}
			on:mouseenter={() => {
				if (!$contextMenuOpen) {
					selectedQuickAccess.set(file)
				}
			}}
			on:mouseleave={() => {
				if (!$contextMenuOpen) {
					selectedQuickAccess.set(null)
				}
			}}
		>
			<div class="flex flex-col w-full h-full px-2 gap-y-2">
				<button
					type="button"
					class="flex items-center gap-x-2"
					on:click={() => {
						appendPath(file.path)
					}}
				>
					<Icon icon={file.type} colored />
					<span
						class="whitespace-nowrap overflow-hidden text-ellipsis text-[#b9b9b9] font-inter hover:font-bold"
						>{file.name}</span
					>
				</button>
			</div>
		</li>
	{/each}
</ul>
