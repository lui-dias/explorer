<script lang="ts">
	import Icon from '../Icon.svelte'

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
		selected?: boolean
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
			if (inner.length < 0) {
				action()
			}
		}}
	>
		<Icon {icon} type="other" />
		<span class="ml-2">{text}</span>

		<div
			class="absolute top-0 left-full dark:bg-zinc-600 w-72"
			class:hidden={!isHovered}
			bind:this={menuList}
		>
			{#each inner as { text, icon, condition, action, selected }}
				{#if condition === undefined || condition()}
					<button
						type="button"
						class={`px-4 py-2 flex justify-between items-center w-full hover:bg-zinc-500 ${
							selected ? 'bg-zinc-600/20' : ''
						}`}
						on:click={action}
					>
						<Icon {icon} type="other" />
						<span class="ml-2">{text}</span>
					</button>
				{/if}
			{/each}
		</div>
	</button>
{/if}
