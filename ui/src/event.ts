import { get } from 'svelte/store'
import {
	cwd,
	cwdSplit,
	explorerItems,
	footer,
	history,
	historyIndex,
	scrollExplorerToBottom,
	selected,
	sortTypeReversed,
} from './store'
import type { TFooter } from './types'
import { debounce, gen_id, py, sortItems } from './utils'

// Without this, the footer will be cleared after 5 seconds
// even if other events are emitted
let footerDebounce = debounce(
	() =>
		footer.set({
			text: '',
			type: 'none',
		}),
	5000,
)

export const E = {
	// Update explorer items
	reload: async () => {
		await py.deleteAllStreamsLs()

		// When creating a file/folder, even using ls, the size of the files was buggy,
		// a file had the size of another file
		// Doing this causes a small flash in explorer, but it solves the problem :/
		explorerItems.set([])

		const $cwd = get(cwd)
		cwdSplit.set($cwd.split('/'))

		await py.startLs($cwd)

		while (true) {
			const r = await py.ls($cwd)

			if (!r) break

			const { end, items: newItems } = r

			const $sortTypeReversed = get(sortTypeReversed)

			explorerItems.update(items => {
				const v = sortItems([...items, ...newItems])

				if ($sortTypeReversed) {
					v.reverse()
				}

				return v
			})

			if (end) {
				break
			}
		}
	},

	// Delete selected items
	delete: async (path: string | string[], moveToTrash: boolean) => {
		const id = gen_id()

		await py.startDelete(id, path, moveToTrash)

		while (true) {
			const r = await py.streamDelete(id)

			if (!r) break

			const { end, total, deleted, last_deleted } = r

			await E.footerText({
				text: `Deleted ${deleted}/${total} ${!!last_deleted ? `- ${last_deleted}` : ''}`,
				type: 'info',
			})

			if (end) {
				break
			}
		}

		selected.set([])
		await E.reload()
	},

	// Set footer text
	footerText: async ({ text, type }: TFooter) => {
		footer.set({
			text,
			type,
		})

		footerDebounce()
	},

	// Back to previous directory in history
	back: async () => {
		const $historyIndex = get(historyIndex)

		if ($historyIndex > 0) {
			historyIndex.set($historyIndex - 1)
		}
	},

	// Forward to next directory in history
	forward: async () => {
		const $historyIndex = get(historyIndex)
		const $history = get(history)

		if ($historyIndex < $history.length - 1) {
			historyIndex.set($historyIndex + 1)
		}
	},

	createNewExplorerFile: async () => {
		const $explorerItems = get(explorerItems)
		const $cwd = get(cwd)
		const $scrollExplorerToBottom = get(scrollExplorerToBottom)

		explorerItems.set([
			...$explorerItems,
			{
				name: 'file',
				path: $cwd + '/file',
				isEditMode: true,
				kind: 'file',
				size: 0,
				parent: $cwd,
				modified: new Date().toISOString(),
				accessed: new Date().toISOString(),
				created: new Date().toISOString(),
				type: 'Text',
				action: 'createFile',
			},
		])

		$scrollExplorerToBottom()
	},

	createNewExplorerFolder: async () => {
		const $explorerItems = get(explorerItems)
		const $cwd = get(cwd)
		const $scrollExplorerToBottom = get(scrollExplorerToBottom)

		explorerItems.set([
			...$explorerItems,
			{
				name: 'folder',
				path: $cwd + '/folder',
				isEditMode: true,
				kind: 'folder',
				size: 0,
				parent: $cwd,
				modified: new Date().toISOString(),
				accessed: new Date().toISOString(),
				created: new Date().toISOString(),
				type: 'Folder',
				action: 'createFolder',
			},
		])

		$scrollExplorerToBottom()
	},
}
