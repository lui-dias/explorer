<script lang="ts">
	import { contextMenuOpen, cwd, explorerItems } from '../../../store'
	import { formatDate } from '../../../utils'
</script>

<ul>
	<li>
		<button
			type="button"
			on:click={() => {
				contextMenuOpen.set(false)

				explorerItems.set([
					...$explorerItems,
					{
						name: 'file',
						path: $cwd + '/file',
						isEditMode: true,
						kind: 'file',
						size: 0,
						parent: $cwd,
						modified: formatDate(new Date()),
						type: 'Text',
						action: 'create_file',
					},
				])
			}}
			class="w-full px-4 py-2 dark:hover:bg-zinc-500"
		>
			File
		</button>
	</li>
	<li>
		<button
			type="button"
			on:click={() => {
				contextMenuOpen.set(false)

				explorerItems.set([
					...$explorerItems,
					{
						name: 'folder',
						path: $cwd + '/folder',
						isEditMode: true,
						kind: 'folder',
						size: 0,
						parent: $cwd,
						modified: formatDate(new Date()),
						type: 'Folder',
						action: 'create_folder',
					},
				])
			}}
			class="w-full px-4 py-2 dark:hover:bg-zinc-500"
		>
			Folder
		</button>
	</li>
</ul>
