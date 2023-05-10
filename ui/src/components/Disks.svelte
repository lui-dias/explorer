<script>
	import { disks } from '../store'
	import { appendPath, formatBytes } from '../utils'
	import Icon from './ui/Icon.svelte'
</script>

<ul class="space-y-3">
	{#each $disks as d}
		<li
			class="group h-[50px] overflow-hidden hover:h-24 transition-all ease-out duration-[400ms]"
		>
			<button type="button" on:click={() => appendPath(d.path)} class="w-full">
				<div class="flex">
					<div class="w-8 flex justify-center items-center">
						{#if d.device === 'Removable Disk'}
							<Icon icon="OtherUsb" colored />
						{:else}
							<Icon icon="OtherDisk" colored />
						{/if}
					</div>

					<div class="w-full flex flex-col gap-y-0.5 ml-2 translate-y-1">
						<span class="text-[#b9b9b9] font-bold leading-4 text-left"
							>{d.name} ({d.path})</span
						>

						<div class="w-full flex justify-between">
							<span class="text-[#7f8388] text-[12px]">{d.device}</span>
							<span class="text-[12px] text-[#b9b9b9]">{d.percent}%</span>
						</div>
					</div>
				</div>

				<div class="mt-2">
					<div class="flex h-1 group-hover:h-6 transition-all duration-[400ms]">
						<div
							class="w-full h-full rounded bg-[rgba(255,255,255,0.5)] text-center font-medium text-white overflow-hidden relative"
						>
							<div class="h-full bg-blue-500" style={`width: ${d.percent}%`} />
							<span class="block absolute inset-0 top-0.5 text-sm">
								{formatBytes(d.used)} Used
							</span>
						</div>
					</div>
				</div>

				<div
					class="text-sm text-[#b9b9b9] text-left font-bold mt-1 opacity-0 group-hover:opacity-100 transition-opacity"
				>
					{formatBytes(d.free)}
					<span class="text-sm text-[#7f8388] font-normal"> free of </span>
					{formatBytes(d.total)}
				</div>
			</button>
		</li>
	{/each}
</ul>
