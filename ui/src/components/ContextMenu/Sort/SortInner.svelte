<script lang="ts">
	import { contextMenuOpen, sortType } from '../../../store'
</script>

<ul>
	<li>
		<button
			type="button"
			on:click={() => {
				sortType.set('name')
				contextMenuOpen.set(false)
			}}
			class={`w-full px-4 py-2 dark:hover:bg-zinc-500 ${
				$sortType === 'name' ? 'dark:bg-purple-300/20' : ''
			}`}
		>
			Name
		</button>
	</li>
	<li>
		<button
			type="button"
			on:click={() => {
				sortType.set('modified')
				contextMenuOpen.set(false)
			}}
			class={`w-full px-4 py-2 dark:hover:bg-zinc-500 ${
				$sortType === 'modified' ? 'dark:bg-purple-300/20' : ''
			}`}
		>
			Modified
		</button>
	</li>
	<li>
		<button
			type="button"
			on:click={() => {
				sortType.set('type')
				contextMenuOpen.set(false)
			}}
			class={`w-full px-4 py-2 dark:hover:bg-zinc-500 ${
				$sortType === 'type' ? 'dark:bg-purple-300/20' : ''
			}`}
		>
			Type
		</button>
	</li>
	<li>
		<button
			type="button"
			on:click={() => {
				sortType.set('size')
				contextMenuOpen.set(false)
			}}
			class={`w-full px-4 py-2 dark:hover:bg-zinc-500 ${
				$sortType === 'size' ? 'dark:bg-purple-300/20' : ''
			}}`}
		>
			Size
		</button>
	</li>
</ul>
