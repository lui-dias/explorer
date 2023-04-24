<script lang="ts">
	import { quickAccess } from '../store'
	import { setPath } from '../utils'
	import Icon from './Icon.svelte'
</script>

<aside class="min-w-[150px] text-primary text-sm border-r border-zinc-700">
	<ul>
		{#each $quickAccess as file}
			<li class="hover:bg-purple-300/20">
				<div class="w-full h-full flex flex-col gap-y-2 px-2">
					<button type="button" class="flex gap-x-2 items-center" on:click={() => {
                        setPath(file)
                    }}>
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
