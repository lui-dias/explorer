<script lang="ts">
	import { onMount } from 'svelte'
	import { Motion } from 'svelte-motion'
	import { E } from '../event'
	import { cwd, isSearching, searchItems } from '../store'
	import { py, outsideClick, sleep } from '../utils'
	import Button from './ui/Button.svelte'
	import Icon from './ui/Icon.svelte'

	let query = ''
	let showSearch = false
	let container: HTMLDivElement
	let input: HTMLInputElement

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
	// This is necessary to avoid create another streamFind when cwd changes
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
				await sleep(0.4)
				si = 0
			}
		})
	})

	$: if (input) {
		input.focus()
	}
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
				data-test-id="search"
				use:motion
			>
				<input
					type="text"
					placeholder="Search"
					class="w-full h-full bg-transparent outline-none px-2 rounded text-[#b9b9b9] placeholder:text-[#b9b9b9]"
					spellcheck="false"
					bind:value={query}
					bind:this={input}
					on:keydown={async e => {
						if (e.key === 'Enter' && query) {
							await py.deleteAllStreamsFind()
							searchItems.set([])

							lastCwd = $cwd
							const q = query
							await py.startFind($cwd, query)
							isSearching.set(true)

							while (true) {
								const r = await py.streamFind($cwd)

								if (!r) break

								const { end, total, files: NewFiles } = r

								E.footerText({
									text: `Searching for '${q}', found ${total} files...`,
									type: 'info',
								})

								searchItems.set([...$searchItems, ...NewFiles])

								if (end || lastCwd !== $cwd) {
									if (!end) {
										// Call last time to set end as true and delete the stream
										await py.streamFind(lastCwd)
									}

									await E.footerText({
										text: `Finished search for ${q}, found ${total} files`,
										type: 'info',
									})

									break
								}
							}

							isSearching.set(false)
						}
					}}
				/>
			</div>
		</Motion>
	{:else}
		<Motion animate={{ scale: s }} transition={{ duration: 0.4, ease: 'easeInOut' }} let:motion>
			<div use:motion>
				<Button
					data-test-id="search-icon"
                    aria-label="Search for files in that folder"
					on:click={async () => {
						si = (si + 1) % 2

						await sleep(0.4)
						ssi = 0
						showSearch = true
					}}
				>
					<Icon icon="OtherSearch" slot="icon" colored glow />
				</Button>
			</div>
		</Motion>
	{/if}
</div>
