<script lang="ts">
	import { contextMenuOpen, quickAccess, selected, selectedQuickAccess } from '../../../store'
</script>

<button
	type="button"
	class="flex justify-between items-center gap-x-3 w-full"
	on:click={() => {
		if ($selectedQuickAccess) {
			quickAccess.set([
				...$quickAccess.filter(
					i => $selectedQuickAccess && i.path !== $selectedQuickAccess.path,
				),
			])
		} else {
			quickAccess.set([...$quickAccess.filter(i => i.path !== $selected[0].path)])
		}
		localStorage.setItem('quickAccess', JSON.stringify($quickAccess.map(item => item.path)))
		contextMenuOpen.set(false)
	}}
>
	Unpin to Quick Access
</button>
