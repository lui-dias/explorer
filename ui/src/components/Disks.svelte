<script>
	import { onMount } from 'svelte'
	import { disks } from '../store'
	import Icon from './ui/Icon.svelte'
	import { formatBytes } from '../utils'
</script>

<ul class="space-y-6">
	{#each $disks as d}
		<li class="group">
			<div class="flex">
				<div class="w-8">
					<Icon icon="OtherDisk" glow={false} />
				</div>

				<div class="w-full flex flex-col ml-2 translate-y-1">
					<span class="text-[#b9b9b9] font-bold leading-4">{d.device}</span>

					<div class="w-full flex justify-between">
						<span class="text-[#7f8388] text-sm">{d.path}</span>
						<span class="text-sm text-[#b9b9b9]">{d.percent}%</span>
					</div>
				</div>
			</div>

			<div class="mt-2">
				<div class="flex h-1 group-hover:h-6 transition-all">
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

			<div class="text-sm text-[#b9b9b9] font-bold mt-1">
				{formatBytes(d.free)}
				<span class="text-sm text-[#7f8388] font-normal"> free of </span>
				{formatBytes(d.total)}
			</div>
		</li>
	{/each}
</ul>
