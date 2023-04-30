<script>
	import { settings, settingsOpen } from '../store'
	import Close from './icons/Close.svelte'
	import Reload from './icons/Reload.svelte'

	$: {
		if (Object.keys($settings).length > 0) {
			document.documentElement.style.setProperty('--primary', $settings.colors.primary)
			document.documentElement.style.setProperty('--accent', $settings.colors.accent)
			document.documentElement.style.setProperty('--text', $settings.colors.text)
			document.documentElement.style.setProperty('--background', $settings.colors.background)
			document.documentElement.style.setProperty('--divider', $settings.colors.divider)
		}
	}
</script>

{#if $settingsOpen}
	<div class="absolute w-full h-[calc(100%-30px)] top-[30px] bg-zinc-700 z-10">
		<div class="w-full px-4">
			<div class="w-full">
				<button
					type="button"
					class="block p-3 ml-auto"
					on:click={() => settingsOpen.set(false)}
				>
					<Close class="fill-text" />
				</button>
			</div>

			<div class="flex flex-col gap-y-3">
				<strong class="text-3xl text-text"> Colors </strong>
				<div class="flex items-center gap-x-3">
					<input
						type="color"
						name="primary-color"
						bind:value={$settings.colors.primary}
						style="--primary: {$settings.colors.primary}"
						class="rounded-full w-10 h-10 appearance-none cursor-pointer [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full"
					/>
					<label for="primary-color" class="font-medium text-text"> Primary </label>
					<button
						type="button"
						on:click={() => {
							$settings.colors.primary = '#fecaca'
							settings.set($settings)
						}}
					>
						<Reload class="stroke-primary" />
					</button>
				</div>

				<div class="flex items-center gap-x-3">
					<input
						type="color"
						name="text-color"
						bind:value={$settings.colors.accent}
						style="--text: {$settings.colors.accent}"
						class="rounded-full w-10 h-10 appearance-none cursor-pointer [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full"
					/>
					<label for="text-color" class="font-medium text-text"> Accent </label>
					<button
						type="button"
						on:click={() => {
							$settings.colors.accent = '#dc2626'
							settings.set($settings)
						}}
					>
						<Reload class="stroke-primary" />
					</button>
				</div>

				<div class="flex items-center gap-x-3">
					<input
						type="color"
						name="text-color"
						bind:value={$settings.colors.text}
						style="--text: {$settings.colors.text}"
						class="rounded-full w-10 h-10 appearance-none cursor-pointer [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full"
					/>
					<label for="text-color" class="font-medium text-text"> Text </label>
					<button
						type="button"
						on:click={() => {
							$settings.colors.text = '#fee2e2'
							settings.set($settings)
						}}
					>
						<Reload class="stroke-primary" />
					</button>
				</div>

				<div class="flex items-center gap-x-3">
					<input
						type="color"
						name="text-color"
						bind:value={$settings.colors.background}
						style="--text: {$settings.colors.background}"
						class="rounded-full w-10 h-10 appearance-none cursor-pointer [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full"
					/>
					<label for="text-color" class="font-medium text-text"> Background </label>
					<button
						type="button"
						on:click={() => {
							$settings.colors.background = '#27272a'
							settings.set($settings)
						}}
					>
						<Reload class="stroke-primary" />
					</button>
				</div>

				<div class="flex items-center gap-x-3">
					<input
						type="color"
						name="text-color"
						bind:value={$settings.colors.divider}
						style="--text: {$settings.colors.divider}"
						class="rounded-full w-10 h-10 appearance-none cursor-pointer [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full"
					/>
					<label for="text-color" class="font-medium text-text"> Divider </label>
					<button
						type="button"
						on:click={() => {
							$settings.colors.divider = '#4b5563'
							settings.set($settings)
						}}
					>
						<Reload class="stroke-primary" />
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
