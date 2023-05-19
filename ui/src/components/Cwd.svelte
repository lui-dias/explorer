<script lang="ts">
	import { onMount } from 'svelte'
	import { E } from '../event'
	import { cwd, cwdSplit, isExplorerFocused, selected } from '../store'
	import { outsideClick, sleep } from '../utils'
	import Reload from './icons/Reload.svelte'
	import CwdItem from './CwdItem.svelte'

	let searchNode: HTMLButtonElement
	let inputSearchNode: HTMLInputElement
	let cwdList: HTMLUListElement
	let hideNItems = 0

	let isSearchSelected = false
	// Without padding some long paths keep appearing under the reload icon
	let padding = 40

	async function fixHorizontalScroll() {
		if (!cwdList) return

		if (cwdList.scrollWidth <= cwdList.clientWidth - padding) {
			hideNItems = 0
		} else {
			while (cwdList.scrollWidth > cwdList.clientWidth) {
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

	$: if ($cwdSplit && cwdList) {
		const observer = new MutationObserver(() => {
			fixHorizontalScroll()

			// Avoid infinite loop when setting hideNItems
			observer.disconnect()
		})
		observer.observe(cwdList, { childList: true })
	}

	onMount(() => {
		fixHorizontalScroll()

		// Close search when clicking outside
		outsideClick(searchNode, () => {
			isSearchSelected = false
		})

		window.addEventListener('resize', () => {
			fixHorizontalScroll()
		})
	})
</script>

<svelte:window
	on:keydown={e => {
		if (e.key === 'Escape') {
			isSearchSelected = false
			selected.set([])
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
			<ul class="flex overflow-x-hidden" bind:this={cwdList}>
				{#each $cwdSplit.slice(hideNItems, $cwdSplit.length) as dir, i}
					<CwdItem {dir} {i} {hideNItems} />
				{/each}
			</ul>
			<button
				type="button"
				class="absolute inset-y-0 right-2"
				data-test-id="cwd-reload"
				on:click={async () => {
					await E.stopAllFind()
					await E.reload()
				}}
			>
				<Reload class="stroke-primary" />
			</button>
		</div>
	{/if}
</button>
