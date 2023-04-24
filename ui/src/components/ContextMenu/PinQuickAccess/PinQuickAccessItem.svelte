<script lang="ts">
	import { contextMenuOpen, quickAccess, selected } from '../../../store'
</script>

<button
	type="button"
	class="flex justify-between items-center gap-x-3 w-full"
	on:click={() => {
        quickAccess.set([...$quickAccess, $selected[0]])
        localStorage.setItem('quickAccess', JSON.stringify($quickAccess.map(item => item.path)))
        contextMenuOpen.set(false)
    }}
>
	Pin to Quick Access
</button>
