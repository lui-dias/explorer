<script>
	import Close from './icons/Close.svelte'
	import { settingsOpen, settings } from '../store'
	import { isClient } from '../utils'
	import { onMount } from 'svelte'
	import Reload from './icons/Reload.svelte'

	let isMounted = false

	$: {
		if (isMounted) {
			document.documentElement.style.setProperty('--primary', $settings.primaryColor)
			document.documentElement.style.setProperty('--text', $settings.textColor)
			localStorage.setItem('settings', JSON.stringify($settings))
		}
	}

	onMount(() => {
		if (isClient()) {
			const localSettings = JSON.parse(localStorage.getItem('settings') ?? '{}')

			settings.set({ ...$settings, ...localSettings })
		}

		isMounted = true
	})
</script>

{#if $settingsOpen}
	<div class="absolute w-full h-[calc(100%-30px)] top-[30px] bg-zinc-700 z-10">
		<div class="w-full px-4">
			<div class="w-full">
				<button
					type="button"
					class="p-3 block ml-auto"
					on:click={() => settingsOpen.set(false)}
				>
					<Close class="fill-purple-200" />
				</button>
			</div>

			<div class="flex flex-col gap-y-3">
				<strong class="text-text text-3xl"> Colors </strong>
				<div class="flex items-center gap-x-3">
					<input
						type="color"
						name="primary-color"
						bind:value={$settings.primaryColor}
						style="--primary: {$settings.primaryColor}"
						class="rounded-full w-10 h-10 appearance-none cursor-pointer [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full"
					/>
					<label for="primary-color" class="text-purple-200 font-medium">
						Primary color
					</label>
					<button
						type="button"
						on:click={() => settings.set({ ...$settings, primaryColor: '#ddd6fe' })}
					>
						<Reload class="stroke-primary" />
					</button>
				</div>
				<div class="flex items-center gap-x-3">
					<input
						type="color"
						name="text-color"
						bind:value={$settings.textColor}
						style="--text: {$settings.textColor}"
						class="rounded-full w-10 h-10 appearance-none cursor-pointer [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full"
					/>
					<label for="text-color" class="text-purple-200 font-medium"> Text color </label>
					<button
						type="button"
						on:click={() => settings.set({ ...$settings, textColor: '#f3e8ff' })}
					>
						<Reload class="stroke-primary" />
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
