<script lang="ts">
	import Icon from '../ui/Icon.svelte'

	export let parentHeight: number
	let isHovered = false

	export let text: string
	export let icon: string
	export let condition = () => true
	export let action = () => {}
	export let inner = [] as {
		text: string
		icon: string
		condition?: () => boolean
		action: () => void
		selected?: () => boolean
		dividerBelow?: boolean
		__useStroke?: boolean
	}[]

	let menuList: HTMLDivElement | null = null
	let btn: HTMLButtonElement | null = null

	$: if (menuList && isHovered !== false) {
		menuList.style.left = `100%`
		menuList.style.top = `0`

		menuList.classList.remove('hidden')
		const bounds = menuList.getBoundingClientRect()

		const x = bounds.left
		const y = bounds.top

		const w = bounds.width
		const h = bounds.height

		const ww = window.innerWidth
		const wh = window.innerHeight

		if (x + w > ww) {
			menuList.style.left = `-${w}px`
		}

		if (y + h > wh) {
			menuList.style.top = `-${h - parentHeight}px`
		}
	}
</script>

<!-- svelte-ignore a11y-mouse-events-have-key-events -->
{#if condition()}
	<button
		type="button"
		class="flex items-center justify-between w-full px-4 py-2"
		on:mouseover={() => (isHovered = true)}
		on:mouseleave={() => (isHovered = false)}
		bind:this={btn}
		on:click={e => {
			if (inner.length === 0) {
				action()
			}
		}}
	>
		<Icon {icon} colored />
		<span class="ml-2">{text}</span>

		{#if isHovered}
			<div
				class="absolute top-0 left-full bg-[#32373e]"
				class:hidden={!isHovered}
				bind:this={menuList}
			>
				{#each inner as { text, icon, condition, action, selected, dividerBelow, __useStroke }}
					{#if condition === undefined || condition()}
						<button
							type="button"
							class={`px-4 py-2 flex items-center w-full ${
								selected?.() ? 'bg-[#474C53]' : ''
							}`}
							on:click={action}
						>
							<span class="w-8">
								{#if __useStroke}
									<Icon {icon} colored class="stroke-primary" />
								{:else}
									<Icon {icon} colored />
								{/if}
							</span>
							<span class="ml-auto pl-6">{text}</span>
						</button>
					{/if}
					{#if dividerBelow}
						<hr class="my-2 mx-4 h-px border-0 bg-[#5D636C]" />
					{/if}
				{/each}
			</div>
		{/if}
	</button>
{/if}
