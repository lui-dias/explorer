import { get } from 'svelte/store'
import {
	contextMenuOpen,
	cwd,
	cwdSplit,
	explorerItems,
	footer,
	history,
	historyIndex,
	scrollExplorerToEnd,
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
	reload: async () => {
		await E.deleteAllStreamsLs()

		// When creating a file/folder, even using ls, the size of the files was buggy,
		// a file had the size of another file
		// Doing this causes a small flash in explorer, but it solves the problem :/
		explorerItems.set([])

		const $cwd = get(cwd)
		cwdSplit.set($cwd.split('/'))

		await E.startLs($cwd)

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

	startLs: async (folder: string) => {
		await py.startLs(folder)
	},

	deleteAllStreamsLs: async () => {
		await py.deleteAllStreamsLs()
	},

	createFile: async (path: string) => {
		await py.createFile(path)
		await E.reload()
	},

	createFolder: async (path: string) => {
		await py.createFolder(path)
		await E.reload()
	},

	rename: async (from: string, to: string) => {
		await py.rename(from, to)
		await E.reload()
	},

	delete: async (path: string | string[], moveToTrash: boolean) => {
		const id = gen_id()

		await py.startDelete(id, path, moveToTrash)

		while (true) {
			const r = await py.streamDelete(id)
            
			if (!r) break
            
			const { end, total, deleted, last_deleted } = r
            
            console.log(1)
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

	footerText: async ({ text, type }: TFooter) => {
		footer.set({
			text,
			type,
		})

		footerDebounce()
	},

	back: async () => {
		const $historyIndex = get(historyIndex)

		if ($historyIndex > 0) {
			historyIndex.set($historyIndex - 1)
		}
	},

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
		const $scrollExplorerToEnd = get(scrollExplorerToEnd)

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
				modified: new Date().toISOString(),
				accessed: new Date().toISOString(),
				created: new Date().toISOString(),
				type: 'Text',
				action: 'createFile',
			},
		])

		$scrollExplorerToEnd()
	},

	createNewExplorerFolder: async () => {
		const $explorerItems = get(explorerItems)
		const $cwd = get(cwd)
		const $scrollExplorerToEnd = get(scrollExplorerToEnd)

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
				modified: new Date().toISOString(),
				accessed: new Date().toISOString(),
				created: new Date().toISOString(),
				type: 'Folder',
				action: 'createFolder',
			},
		])

		$scrollExplorerToEnd()
	},
	copy: async (paths: string[]) => {
		await py.copy(paths.join(' '))
	},
	paste: async (folder: string) => {
		await py.paste(folder)
	},
}
