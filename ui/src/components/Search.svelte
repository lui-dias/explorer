<script lang="ts">
	import { onMount } from 'svelte'
	import { events } from '../event'
	import { cwd, isSearching, searchItems } from '../store'
	import { __pywebview, outsideClick } from '../utils'
	import SearchIcon from './icons/SearchIcon.svelte'

	let query = ''
	let showSearch = false
	let container: HTMLDivElement

	// This is necessary to avoid create another stream_find when cwd changes
	let lastCwd = ''

	onMount(() => {
		outsideClick(container, () => {
			showSearch = false
		})
	})
</script>

<div bind:this={container}>
	{#if showSearch}
		<div class="w-full h-8 ml-2 dark:bg-zinc-700">
			<input
				type="text"
				placeholder="Search"
				class="w-full h-full bg-transparent outline-none px-2 focus:outline-purple-300 dark:placeholder:text-violet-200 dark:text-violet-200"
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
	{:else}
		<button
			type="button"
			class="neuBtn flex items-center justify-center p-2.5 rounded-full"
			on:click={() => (showSearch = true)}
		>
			<SearchIcon class="fill-primary drop-shadow-[0_0_5px_#fecaca] unsetFilterClick" />
		</button>
	{/if}
</div>


