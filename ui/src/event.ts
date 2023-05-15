import { get } from 'svelte/store'
import {
	contextMenuOpen,
	cwd,
	cwdSplit,
	explorerItems,
	footer,
	history,
	historyIndex,
	isSearching,
	scrollExplorerToEnd,
	selected,
	sortTypeReversed,
} from './store'
import type { TFooter } from './types'
import { __pywebview, debounce, formatDate, gen_id, sortItems } from './utils'

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

		isSearching.set(true)

		// When creating a file/folder, even using ls, the size of the files was buggy,
		// a file had the size of another file
		// Doing this causes a small flash in explorer, but it solves the problem :/
		explorerItems.set([])

		const $cwd = get(cwd)
		cwdSplit.set($cwd.split('/'))

		await E.startLs($cwd)

		while (true) {
			const { end, items: newItems } = await __pywebview.ls($cwd)
			const $sortTypeReversed = get(sortTypeReversed)

			explorerItems.update(items => {
				const v = sortItems([...items, ...newItems])

				if ($sortTypeReversed) {
					v.reverse()
				}

				return v
			})

			if (end) {
				isSearching.set(false)

				break
			}
		}
	},

	startLs: async (folder: string) => {
		await __pywebview.start_ls(folder)
	},

	stopAllDelete: async () => {
		await __pywebview.stop_all_streams_delete()
	},

	stopAllFileSize: async () => {
		await __pywebview.stop_all_streams_file_size()
	},

	stopAllFind: async () => {
		await __pywebview.stop_all_streams_find()
	},

	stopAllStreamsLs: async () => {
		await __pywebview.stop_all_streams_ls()
	},

	deleteAllStreamsLs: async () => {
		await __pywebview.delete_all_streams_ls()
	},

	createFile: async (path: string) => {
		await __pywebview.create_file(path)
		await E.reload()
	},

	createFolder: async (path: string) => {
		await __pywebview.create_folder(path)
		await E.reload()
	},

	rename: async (from: string, to: string) => {
		await __pywebview.rename(from, to)
		await E.reload()
	},

	delete: async (path: string | string[], moveToTrash: boolean) => {
		const id = gen_id()

		while (true) {
			const { end, total, deleted, last_deleted } = await __pywebview.stream_delete(
				id,
				path,
				moveToTrash,
			)

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
		await __pywebview.copy(paths.join(' '))
	},
    paste: async (folder: string) => {
        await __pywebview.paste(folder)
    }
}
