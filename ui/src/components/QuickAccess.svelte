<script lang="ts">
	import { onMount } from 'svelte'
	import { contextMenuOpen, quickAccess, selectedQuickAccess } from '../store'
	import { __pywebview, setPath } from '../utils'
	import Icon from './Icon.svelte'
	import { events } from '../event'

	onMount(async () => {
		const items = JSON.parse(localStorage.getItem('quickAccess') ?? '[]') as string[]
		const files = await Promise.all(
			items.map(async item => await __pywebview.get_path_info(item)),
		)

		quickAccess.set(files)
	})
</script>

<aside class="w-full h-full text-sm text-text">
	<ul>
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
							setPath(file.path)
							events.emit('quickAccessClick')
						}}
					>
						<Icon icon={file} />
						<span
							class="whitespace-nowrap overflow-hidden text-ellipsis text-[#b9b9b9] font-inter hover:font-bold"
							>{file.name}</span
						>
					</button>
				</div>
			</li>
		{/each}
	</ul>
</aside>
