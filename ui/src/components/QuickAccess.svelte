<script lang="ts">
	import { onMount } from 'svelte'
	import { quickAccess, selectedQuickAccess } from '../store'
	import { __pywebview, setPath } from '../utils'
	import Icon from './Icon.svelte'

	onMount(async () => {
		const items = JSON.parse(localStorage.getItem('quickAccess') ?? '[]') as string[]
		const files = await Promise.all(
			items.map(async item => await __pywebview.get_path_info(item)),
		)

		quickAccess.set(files)
	})
</script>

<aside class="min-w-[150px] text-text text-sm border-r border-divider">
	<ul>
		{#each $quickAccess as file}
			<li
				class={`hover:bg-purple-300/20 ${
					$selectedQuickAccess?.path === file.path ? 'bg-purple-300/20' : ''
				}`}
				on:mouseenter={() => {
					selectedQuickAccess.set(file)
				}}
			>
				<div class="w-full h-full flex flex-col gap-y-2 px-2">
					<button
						type="button"
						class="flex gap-x-2 items-center"
						on:click={() => {
							setPath(file.path)
						}}
					>
						<Icon {file} />
						<span class="whitespace-nowrap overflow-hidden text-ellipsis"
							>{file.name}</span
						>
					</button>
				</div>
			</li>
		{/each}
	</ul>
</aside>
