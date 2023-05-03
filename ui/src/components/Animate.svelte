<script lang="ts">
	import { Motion } from 'svelte-motion'

	export let initial = {}
	export let animate = {} as Record<string, any[]>
	export let transition = {}

	let motionAnimate = {}
	let index = 0
	export const cycle = () => (index = (index + 1) % (Object.keys(animate).length + 1))

	$: motionAnimate = Object.fromEntries(Object.entries(animate).map(([k, v]) => [k, v[index]]))
</script>

<Motion {initial} animate={motionAnimate} {transition} let:motion>
	<slot {motion} />
</Motion>
