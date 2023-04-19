<script lang="ts">
	import { contextMenuOpen } from '../../../stores/explorerStore'
</script>

<ul>
	<li>
		<button
			type="button"
			on:click={() => {
				contextMenuOpen.set(false)
			}}
			class="w-full px-4 py-2 dark:hover:bg-zinc-500"
		>
			Folder
		</button>
	</li>
	<li>
		<button
			type="button"
			on:click={() => {
				contextMenuOpen.set(false)
			}}
			class="w-full px-4 py-2 dark:hover:bg-zinc-500"
		>
			File
		</button>
	</li>
</ul>
