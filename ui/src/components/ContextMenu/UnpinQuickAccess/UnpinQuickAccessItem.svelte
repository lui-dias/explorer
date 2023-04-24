<script lang="ts">
	import { quickAccess, selected } from '../../../store'
</script>

<button
	type="button"
	class="flex justify-between items-center gap-x-3 w-full"
	on:click={() => {
		if ($quickAccess.some(i => i.path === $selected[0].path)) {
			quickAccess.set([...$quickAccess.filter(i => i.path !== $selected[0].path)])
		}
	}}
>
	Unpin to Quick Access
</button>
