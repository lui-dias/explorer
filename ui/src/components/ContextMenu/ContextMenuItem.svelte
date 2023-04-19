<script lang="ts">
	export let parentHeight: number
	let isHovered = false

	let menuList: HTMLDivElement | null = null

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
<button
	type="button"
	class="px-4 py-2 flex items-center"
	on:mouseover={() => (isHovered = true)}
	on:mouseleave={() => (isHovered = false)}
>
	<slot name="item" />

	<div
		class="absolute top-0 left-full dark:bg-zinc-600 w-72"
		class:hidden={!isHovered}
		bind:this={menuList}
	>
		<slot name="inner" />
	</div>
</button>
