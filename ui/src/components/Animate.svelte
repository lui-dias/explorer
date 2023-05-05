<script lang="ts">
	import {
		Motion,
		type AnimationControls,
		type Target,
		type TargetAndTransition,
		type Transition,
	} from 'svelte-motion'

	export let initial = {} as Target
	export let animate = {} as TargetAndTransition | AnimationControls
	export let transition = {} as Transition

	let motionAnimate = {}
	let index = 0
	export const cycle = () => (index = (index + 1) % (Object.keys(animate).length + 1))
    export const setIndex = (i: number) => (index = i)

	$: motionAnimate = Object.fromEntries(Object.entries(animate).map(([k, v]) => [k, v[index]]))
</script>

<Motion {initial} animate={motionAnimate} {transition} let:motion>
	<slot {motion} />
</Motion>
