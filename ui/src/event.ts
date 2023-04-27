import { get } from 'svelte/store'
import { TypedEmitter } from 'tiny-typed-emitter'
import { cwd, cwdSplit, explorerItems, footer, historyIndex, selected, history } from './store'
import type { TFooter } from './types'
import { __pywebview, debounce, gen_id, sortItems } from './utils'

export const events = new TypedEmitter<{
	create_file: (path: string) => Promise<void>
	create_folder: (path: string) => Promise<void>
	rename: (from: string, to: string) => Promise<void>
	delete: (path: string | string[], moveToTrash: boolean) => Promise<void>
	reload: () => Promise<void>
	footer_text: ({ text, type }: TFooter) => Promise<void>
    stop_stream_delete: (path: string) => Promise<void>
    stop_stream_file_size: (path: string) => Promise<void>
    stop_stream_find: (path: string) => Promise<void>
    stop_all_delete: () => Promise<void>
    stop_all_file_size: () => Promise<void>
    stop_all_find: () => Promise<void>
    end_of_stream_find: () => Promise<void>
    back: () => Promise<void>
    forward: () => Promise<void>
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

events.on('create_file', async (file: string) => {
	await __pywebview.create_file(file)
	events.emit('reload')
})

events.on('create_folder', async (folder: string) => {
	await __pywebview.create_folder(folder)
	events.emit('reload')
})

events.on('rename', async (from: string, to: string) => {
	await __pywebview.rename(from, to)
	events.emit('reload')
})

events.on('delete', async (path: string | string[], moveToTrash: boolean) => {
	const id = gen_id()

	while (true) {
		const { end, total, deleted, last_deleted } = await __pywebview.stream_delete(
			id,
			path,
			moveToTrash,
		)
		events.emit('footer_text', {
			text: `Deleted ${deleted}/${total} ${!!last_deleted ? `- ${last_deleted}` : ''}`,
			type: 'info',
		})

		if (end) {
			break
		}
	}

	events.emit('reload')
	selected.set([])
})

events.on('reload', async () => {
	const $cwd = get(cwd)
	cwdSplit.set($cwd.split('/'))

	// When creating a file/folder, even using ls, the size of the files was buggy,
	// a file had the size of another file
	// Doing this causes a small flash in explorer, but it solves the problem :/
	explorerItems.set([])
	explorerItems.set(sortItems(await __pywebview.ls($cwd)))
})

events.on('footer_text', async ({ text, type }: TFooter) => {
	footer.set({
		text,
		type,
	})

	footerDebounce()
})

events.on('stop_stream_delete', async (path: string) => {
    await __pywebview.stop_stream_delete(path)
})

events.on('stop_stream_file_size', async (path: string) => {
    await __pywebview.stop_stream_file_size(path)
})

events.on('stop_stream_find', async (path: string) => {
    await __pywebview.stop_stream_find(path)
})

events.on('stop_all_delete', async () => {
    await __pywebview.stop_all_streams_delete()
})

events.on('stop_all_file_size', async () => {
    await __pywebview.stop_all_streams_file_size()
})

events.on('stop_all_find', async () => {
    await __pywebview.stop_all_streams_find()

    events.emit('end_of_stream_find')
})

events.on('back', async () => {
    const $historyIndex = get(historyIndex)

    if ($historyIndex > 0) {
        historyIndex.set($historyIndex - 1)
    }
})

events.on('forward', async () => {
    const $historyIndex = get(historyIndex)
    const $history = get(history)

    if ($historyIndex < $history.length - 1) {
        historyIndex.set($historyIndex + 1)
    }
})