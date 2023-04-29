<script lang="ts">
	import { onMount } from 'svelte'
	import { quickAccess, selectedQuickAccess } from '../store'
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

<aside class="w-full h-full text-text text-sm">
	<ul>
		{#each $quickAccess as file}
			<li
				class={`pl-4 hover:font-bold hover:scale-[115%] transition-transform ${
					$selectedQuickAccess?.path === file.path ? 'font-bold' : ''
				}`}
				on:mouseenter={() => {
					selectedQuickAccess.set(file)
				}}
				on:mouseleave={() => {
					selectedQuickAccess.set(null)
				}}
			>
				<div class="w-full h-full flex flex-col gap-y-2 px-2">
					<button
						type="button"
						class="flex gap-x-2 items-center"
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
