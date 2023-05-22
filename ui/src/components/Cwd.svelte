<script lang="ts">
	import { onMount } from 'svelte'
	import { E } from '../event'
	import { cwd, cwdSplit, isExplorerFocused } from '../store'
	import { outsideClick, py, sleep } from '../utils'
	import CwdItem from './CwdItem.svelte'
	import Reload from './icons/Reload.svelte'

	let searchNode: HTMLButtonElement
	let inputSearchNode: HTMLInputElement
	let cwdListNode: HTMLUListElement
	/** How many items of cwd should be hidden */
	let hideNItems = 0

	let isSearchSelected = false
	// Without padding some long paths keep appearing under the reload icon
	let padding = 40

	async function fixHorizontalScroll() {
		if (!cwdListNode) return

		if (cwdListNode.scrollWidth <= cwdListNode.clientWidth - padding) {
			hideNItems = 0
		} else {
			// While have scrollbar
			while (cwdListNode.scrollWidth > cwdListNode.clientWidth) {
				// This is necessary to avoid infinite loop
				await sleep(0)

				hideNItems += 1
			}
		}
	}

	// Focus search input when search button is clicked
	$: if (inputSearchNode) {
		inputSearchNode.focus()
	}

	$: if ($cwdSplit && cwdListNode) {
		const observer = new MutationObserver(() => {
			fixHorizontalScroll()

			// Avoid infinite loop when setting hideNItems
			observer.disconnect()
		})
		observer.observe(cwdListNode, { childList: true })
	}

	onMount(() => {
		fixHorizontalScroll()

		// Close search when clicking outside
		outsideClick(searchNode, () => {
			isSearchSelected = false
		})

		window.addEventListener('resize', fixHorizontalScroll)
	})
</script>

<svelte:window
	on:keydown={e => {
		if (e.key === 'Escape') {
			isSearchSelected = false
		}
	}}
/>

<button
	type="button"
	data-test-id="cwd"
	id="cwd"
	class="dark:bg-zinc-700 w-full text-[#b9b9b9] flex items-center overflow-x-auto transition-transform duration-[250ms]"
	class:scale-[101%]={isSearchSelected}
	style="border-radius: 12px;
    background: linear-gradient(145deg, #32383b, #2a2f32);
    box-shadow:  4px 4px 8px #24282a,
                 -4px -4px 8px #3a4044;"
	on:focus={() => {
		isSearchSelected = true
		isExplorerFocused.set(false)
	}}
	on:click={() => {
		isExplorerFocused.set(false)
	}}
	bind:this={searchNode}
>
	{#if isSearchSelected}
		<input
			type="text"
			class="w-full h-10 px-2 tracking-wide bg-transparent outline-none focus:outline-purple-300"
			value={$cwd}
			data-test-id="cwd-input"
			on:keyup={async e => {
				if (e.key === 'Enter') {
					cwd.set(inputSearchNode.value)
					await E.reload()
				}
			}}
			bind:this={inputSearchNode}
		/>
	{:else}
		<div class="relative w-full">
			<ul class="flex overflow-x-hidden" bind:this={cwdListNode}>
				{#each $cwdSplit.slice(hideNItems, $cwdSplit.length) as dir, i}
					<CwdItem {dir} cwdItemIndex={i} {hideNItems} />
				{/each}
			</ul>
			<button
				type="button"
				class="absolute inset-y-0 right-2"
				data-test-id="cwd-reload"
				aria-label="Reload explorer"
				on:click={async () => {
					await py.deleteAllStreamsFind()
					await E.reload()
				}}
			>
				<Reload class="stroke-primary" />
			</button>
		</div>
	{/if}
</button>
