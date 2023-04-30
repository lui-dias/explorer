<script lang="ts">
	import { onMount } from 'svelte'
	import { Motion } from 'svelte-motion'
	import { events } from '../event'
	import { cwd, isSearching, searchItems } from '../store'
	import { __pywebview, outsideClick, sleep } from '../utils'
	import SearchIcon from './icons/SearchIcon.svelte'

	let query = ''
	let showSearch = false
	let container: HTMLDivElement

	let s = [1]
	let ss = [1]
	let si = 0
	let ssi = 0

	$: {
		s = [
			[1, 1, 1, 1],
			[1, 1.25, 0, 0],
			[0, 1, 1.15, 1],
		][si]
		ss = [
			[0, 1],
			[1, 0],
		][ssi]
	}
	// This is necessary to avoid create another stream_find when cwd changes
	let lastCwd = ''

	onMount(() => {
		outsideClick(container, async () => {
			if (showSearch) {
				// Hide search
				ssi = 1
				await sleep(0.2)

				// Show button
				showSearch = false
				si = 2

				// Reset search
				await sleep(0.5)
				si = 0
			}
		})
	})
</script>

<div bind:this={container}>
	{#if showSearch}
		<Motion
			initial={{ opacity: 0 }}
			animate={{ opacity: ss }}
			transition={{ duration: 0.2 }}
			let:motion
		>
			<div
				class="w-full h-10 ml-2 dark:bg-[#32373a] rounded relative neuBorder"
				style:transform-origin="top left"
				use:motion
			>
				<input
					type="text"
					placeholder="Search"
					class="w-full h-full bg-transparent outline-none px-2 rounded text-[#b9b9b9] placeholder:text-[#b9b9b9]"
					spellcheck="false"
					autocomplete="false"
					bind:value={query}
					on:keydown={e => {
						if (e.key === 'Enter' && query) {
							events.once('end_of_stream_find', async () => {
								if (lastCwd) {
									await __pywebview.stream_find(lastCwd, query)
									searchItems.set([])
								}

								lastCwd = $cwd
								const q = query
								isSearching.set(true)

								while (true) {
									const {
										end,
										total,
										files: NewFiles,
									} = await __pywebview.stream_find($cwd, query)

									events.emit('footer_text', {
										text: `Searching for '${q}', found ${total} files...`,
										type: 'info',
									})

									searchItems.set(NewFiles)

									if (end || lastCwd !== $cwd) {
										if (!end) {
											// Call last time to set end as true and delete the stream
											await __pywebview.stream_find(lastCwd, query)
										}

										events.emit('footer_text', {
											text: `Finished search for ${q}, found ${total} files`,
											type: 'info',
										})

										break
									}
								}

								isSearching.set(false)
							})

							events.emit('stop_all_find')
						}
					}}
				/>
			</div>
		</Motion>
	{:else}
		<Motion
			animate={{ scale: s }}
			transition={{ duration: 0.45, ease: 'easeInOut' }}
			let:motion
		>
			<button
				type="button"
				class="neuBtn flex items-center justify-center p-2.5 rounded-full"
				on:click={async () => {
					si = (si + 1) % 2

					await sleep(0.5)
					ssi = 0
					showSearch = true
				}}
				use:motion
			>
				<span class="glow">
					<SearchIcon class="fill-primary " />
				</span>
			</button>
		</Motion>
	{/if}
</div>
