import { get } from 'svelte/store'
import { TypedEmitter } from 'tiny-typed-emitter'
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
} from './store'
import type { TFooter } from './types'
import { __pywebview, debounce, formatDate, gen_id, sleep, sortItems } from './utils'

// prettier-ignore
export const events = new TypedEmitter<{
    createFile        : (path: string) => Promise<void>
    createFolder      : (path: string) => Promise<void>
    rename            : (from: string, to: string) => Promise<void>
    delete            : (path: string | string[], moveToTrash: boolean) => Promise<void>
    reload            : () => Promise<void>
    footerText        : ({ text, type }: TFooter) => Promise<void>
    stopStreamDelete  : (path: string) => Promise<void>
    stopStreamFileSize: (path: string) => Promise<void>
    stopStreamFind    : (path: string) => Promise<void>
    stopAllDelete     : () => Promise<void>
    stopAllFileSize   : () => Promise<void>
    stopAllFind       : () => Promise<void>
    stopAllStreamsLs  : () => Promise<void>
    endOfStreamFind   : () => Promise<void>
    endOfStreamLs     : () => Promise<void>
    back              : () => Promise<void>
    forward           : () => Promise<void>
    cwdClick          : (path: string) => Promise<void>
    quickAccessClick  : () => Promise<void>
    backClick         : () => Promise<void>
    forwardClick      : () => Promise<void>
    windowButtonsClick: () => Promise<void>
    itemClick         : () => Promise<void>
    itemDoubleClick   : () => Promise<void>
    stopFindAndReload : () => Promise<void>
    createNewFile     : () => Promise<void>
    createNewFolder   : () => Promise<void>
    end               : (e:
        | 'createFile'
        | 'createFolder'
        | 'rename'
        | 'delete'
        | 'reload'
        | 'footerText'
        | 'stopStreamDelete'
        | 'stopStreamFileSize'
        | 'stopStreamFind'
        | 'stopAllDelete'
        | 'stopAllFileSize'
        | 'stopAllFind'
        | 'stopAllStreamsLs'
        | 'endOfStreamFind'
        | 'endOfStreamLs'
        | 'back'
        | 'forward'
        | 'cwdClick'
        | 'quickAccessClick'
        | 'backClick'
        | 'forwardClick'
        | 'windowButtonsClick'
        | 'itemClick'
        | 'itemDoubleClick'
        | 'stopFindAndReload'
        | 'createNewFile'
        | 'createNewFolder'
        | 'end'
    ) => Promise<void>
}>()

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

events.on('createFile', async (file: string) => {
	await __pywebview.create_file(file)
	events.emit('reload')
	events.emit('end', 'createFile')
})

events.on('createFolder', async (folder: string) => {
	await __pywebview.create_folder(folder)
	events.emit('reload')
	events.emit('end', 'createFolder')
})

events.on('rename', async (from: string, to: string) => {
	await __pywebview.rename(from, to)
	events.emit('reload')
	events.emit('end', 'rename')
})

events.on('delete', async (path: string | string[], moveToTrash: boolean) => {
	const id = gen_id()

	while (true) {
		const { end, total, deleted, last_deleted } = await __pywebview.stream_delete(
			id,
			path,
			moveToTrash,
		)
		events.emit('footerText', {
			text: `Deleted ${deleted}/${total} ${!!last_deleted ? `- ${last_deleted}` : ''}`,
			type: 'info',
		})

		if (end) {
			break
		}
	}

	events.emit('reload')
	selected.set([])
	events.emit('end', 'delete')
})

const queue = {
	actualWorker: 0,
	waitingWorker: 0,
}

events.on('cwdClick', async () => {
	queue.waitingWorker += 1
})
events.on('quickAccessClick', async () => {
	queue.waitingWorker += 1
})
events.on('itemDoubleClick', async () => {
	queue.waitingWorker += 1
})

events.on('reload', async () => {
	const $cwd = get(cwd)
	cwdSplit.set($cwd.split('/'))
	isSearching.set(true)

	// When creating a file/folder, even using ls, the size of the files was buggy,
	// a file had the size of another file
	// Doing this causes a small flash in explorer, but it solves the problem :/
	explorerItems.set([])

	async function _(ev: any) {
		if (ev === 'stopAllStreamsLs') {
			while (queue.actualWorker) await sleep(0)

			queue.actualWorker = 1
			queue.waitingWorker = Math.max(0, queue.waitingWorker - 1)

			while (true) {
				const { end, items: newItems } = await __pywebview.ls($cwd)

				explorerItems.update(items => sortItems([...items, ...newItems]))

				if (end || queue.waitingWorker) {
					if (queue.waitingWorker) {
						explorerItems.set([])
					} else {
						isSearching.set(false)
					}

					queue.actualWorker = 0

					break
				}
			}

            // @ts-ignore
			events.off('stopAllStreamsLs', _)
			events.emit('end', 'reload')
		}
	}
	events.emit('stopAllStreamsLs')
	events.on('end', _)
})

events.on('footerText', async ({ text, type }: TFooter) => {
	footer.set({
		text,
		type,
	})

	footerDebounce()
	events.emit('end', 'footerText')
})

events.on('stopStreamDelete', async (path: string) => {
	await __pywebview.stop_stream_delete(path)
	events.emit('end', 'stopStreamDelete')
})

events.on('stopStreamFileSize', async (path: string) => {
	await __pywebview.stop_stream_file_size(path)
	events.emit('end', 'stopStreamFileSize')
})

events.on('stopStreamFind', async (path: string) => {
	await __pywebview.stop_stream_find(path)
	events.emit('end', 'stopStreamFind')
})

events.on('stopAllDelete', async () => {
	await __pywebview.stop_all_streams_delete()
	events.emit('end', 'stopAllDelete')
})

events.on('stopAllFileSize', async () => {
	await __pywebview.stop_all_streams_file_size()
	events.emit('end', 'stopAllFileSize')
})

events.on('stopAllFind', async () => {
	await __pywebview.stop_all_streams_find()
	events.emit('end', 'stopAllFind')
})

events.on('stopAllStreamsLs', async () => {
	await __pywebview.stop_all_streams_ls()
	events.emit('end', 'stopAllStreamsLs')
})

events.on('back', async () => {
	const $historyIndex = get(historyIndex)

	if ($historyIndex > 0) {
		historyIndex.set($historyIndex - 1)
	}

	events.emit('end', 'back')
})

events.on('forward', async () => {
	const $historyIndex = get(historyIndex)
	const $history = get(history)

	if ($historyIndex < $history.length - 1) {
		historyIndex.set($historyIndex + 1)
	}

	events.emit('end', 'forward')
})

events.on('stopFindAndReload', async () => {
	events.emit('stopAllFind')

	events.once('end', async ev => {
		if (ev === 'stopFindAndReload') events.emit('reload')
	})

	events.emit('end', 'stopFindAndReload')
})

events.on('createNewFile', async () => {
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
			modified: formatDate(new Date()),
			type: 'Text',
			action: 'createFile',
		},
	])

	$scrollExplorerToEnd()
	events.emit('end', 'createNewFile')
})

events.on('createNewFolder', async () => {
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
			modified: formatDate(new Date()),
			type: 'Folder',
			action: 'createFolder',
		},
	])

	$scrollExplorerToEnd()
	events.emit('end', 'createNewFolder')
})
