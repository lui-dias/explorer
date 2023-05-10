import { get } from 'svelte/store'
import { cwd, cwdSplit, history, historyIndex, sortType } from './store'
import type { ExplorerItem, TConfig, TDisksInfo } from './types'

const isVisible = (elem: any) =>
	!!elem && !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length)

export function outsideClick(node: any, callback: any) {
	const handleClick = (event: any) => {
		if (node && !node.contains(event.target) && !event.defaultPrevented && isVisible(node)) {
			callback(event)
		}
	}

	document.addEventListener('click', handleClick, true)

	return {
		destroy() {
			document.removeEventListener('click', handleClick, true)
		},
	}
}

export function sort<T>(arr: T[], fn: (key: T) => any, reverse = false) {
	const copy = [...arr]

	return copy.sort((a, b) => {
		const aKey = fn(a)
		const bKey = fn(b)

		if (aKey === bKey) {
			return 0
		}

		if (aKey > bKey) {
			return reverse ? -1 : 1
		}

		return reverse ? 1 : -1
	})
}

export function formatBytes(bytes: number) {
	if (bytes < 1000) {
		return `${bytes} B`
	}

	if (bytes < 1000 ** 2) {
		return `${(bytes / 1000).toFixed(2)} KB`
	}

	if (bytes < 1000 ** 3) {
		return `${(bytes / 1000 ** 2).toFixed(2)} MB`
	}

	if (bytes < 1000 ** 4) {
		return `${(bytes / 1000 ** 3).toFixed(2)} GB`
	}

	return `${(bytes / 1000 ** 4).toFixed(2)} TB`
}

export function isNumber(value: string) {
	return !isNaN(Number(value))
}

export function formatDate(date: Date) {
	const formats = {
		yyyy: date.getFullYear(),
		MM: date.getMonth() + 1,
		dd: date.getDate(),
		HH: date.getHours(),
		mm: date.getMinutes(),
		ss: date.getSeconds(),
	} as Record<string, number>

	return Object.keys(formats).reduce((acc, key) => {
		return acc.replace(key, String(formats[key]).padStart(2, '0'))
	}, 'dd/MM/yyyy HH:mm')
}

export const __pywebview = {
	__wait: async () => {
		const interval = setInterval(() => {
			// @ts-ignore
			if (window.pywebview) {
				clearInterval(interval)
			}
		}, 100)
	},
	close: async (): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.close()
	},
	minimize: async (): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.minimize()
	},
	maximize: async (): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.maximize()
	},
	start_ls: async (folder: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.start_ls(folder)
	},
	ls: async (
		folder: string,
	): Promise<{
		items: ExplorerItem[]
		end: boolean
	}> => {
		// @ts-ignore
		return await pywebview.api.ls(folder)
	},
	home: async (): Promise<string> => {
		// @ts-ignore
		return await pywebview.api.home()
	},
	rename: async (from: string, to: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.rename(from, to)
	},
	create_file: async (path: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.create_file(path)
	},
	create_folder: async (path: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.create_folder(path)
	},
	exists: async (path: string, ignore?: string): Promise<boolean> => {
		// @ts-ignore
		return await pywebview.api.exists(path, ignore)
	},
	stream_folder_size: async (
		path: string,
	): Promise<{
		size: number
		end: boolean
	}> => {
		// @ts-ignore
		return await pywebview.api.stream_folder_size(path)
	},
	stream_delete: async (
		id: string,
		path: string | string[],
		moveToTrash: boolean,
	): Promise<{
		end: boolean
		total: number
		deleted: number
		last_deleted: string
	}> => {
		// @ts-ignore
		return await pywebview.api.stream_delete(id, path, moveToTrash)
	},

	stream_find: async (
		path: string,
		query: string,
	): Promise<{
		end: boolean
		total: number
		files: ExplorerItem[]
	}> => {
		// @ts-ignore
		return await pywebview.api.stream_find(path, query)
	},

	stop_stream_delete: async (path: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.stop_stream_delete(path)
	},

	stop_stream_file_size: async (path: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.stop_stream_file_size(path)
	},

	stop_stream_find: async (path: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.stop_stream_find(path)
	},

	stop_all_streams_delete: async (): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.stop_all_streams_delete()
	},

	stop_all_streams_file_size: async (): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.stop_all_streams_file_size()
	},

	stop_all_streams_find: async (): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.stop_all_streams_find()
	},

	stop_all_streams_ls: async (): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.stop_all_streams_ls()
	},

	delete_all_streams_ls: async () => {
		// @ts-ignore
		return await pywebview.api.delete_all_streams_ls()
	},

	get_path_info: async (path: string): Promise<ExplorerItem> => {
		// @ts-ignore
		return await pywebview.api.get_path_info(path)
	},

	get_config: async (): Promise<TConfig> => {
		// @ts-ignore
		return await pywebview.api.get_config()
	},

	set_config: async (config: TConfig): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.set_config(config)
	},

	read: async (path: string): Promise<string> => {
		// @ts-ignore
		return await pywebview.api.read(path)
	},
	user: async () => {
		// @ts-ignore
		return await pywebview.api.user()
	},
	pwd: async () => {
		// @ts-ignore
		return await pywebview.api.pwd()
	},
	setupTests: async () => {
		// @ts-ignore
		return await pywebview.api.setup_tests()
	},
	clearTests: async () => {
		// @ts-ignore
		return await pywebview.api.clear_tests()
	},
	disksInfo: async (): Promise<TDisksInfo[]> => {
		// @ts-ignore
		return await pywebview.api.disks_info()
	},
	get: async (key: string): Promise<any> => {
		// @ts-ignore
		return await pywebview.api.get(key)
	},
	set: async (key: string, value: any): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.set(key, value)
	},
	getFontWeight: async (path: string): Promise<number | null> => {
		// @ts-ignore
		return await pywebview.api.get_font_weight(path)
	},
}

export function isClient() {
	return typeof window !== 'undefined'
}

export function debounce(fn: () => void, s: number) {
	let timeout: NodeJS.Timeout

	return () => {
		clearTimeout(timeout)
		timeout = setTimeout(fn, s)
	}
}

export function gen_id(size: number = 6) {
	const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
	let id = ''

	for (let i = 0; i < size; i++) {
		id += chars.charAt(Math.floor(Math.random() * chars.length))
	}

	return id
}

export function sleep(s: number) {
	return new Promise(resolve => setTimeout(resolve, s * 1000))
}

export function appendPath(path: string) {
	const hi = get(historyIndex)
	const h = get(history)

	if (hi === h.length - 1) {
		history.set([...h, path])
	} else {
		history.set(h.slice(0, hi + 1).concat(path))
	}

	historyIndex.set(hi + 1)
	cwd.set(path)
}

// Add each parent path to history
// Example: /home/user/Downloads
// history: ['/home', '/home/user', '/home/user/Downloads']
export function setPath(path: string) {
	const $cwdSplit = path.split('/')

	const h = [] as string[]
	for (let i = 0; i < $cwdSplit.length; i++) {
		h.push($cwdSplit.slice(0, i + 1).join('/'))
	}
	history.set(h)
	historyIndex.set($cwdSplit.length - 1)

	cwd.set(path)
	cwdSplit.set($cwdSplit)
}

export function sortItems(items: ExplorerItem[]) {
	const $sortType = get(sortType)

	if ($sortType === 'name') {
		return sort(items, i => (isNumber(i.name) ? Number(i.name) : i.name))
	}
	if ($sortType === 'modified') {
		return sort(items, i => i.modified)
	}
	if ($sortType === 'type') {
		return sort(items, i => i.kind)
	}
	if ($sortType === 'size') {
		return sort(items, i => i.size)
	}

	return items
}

export const b64ToUint8Array = (b64: string) => {
	return Uint8Array.from(atob(b64), c => c.charCodeAt(0))
}

export function assert(condition: boolean, message: string) {
	if (!condition) {
		throw new Error(message)
	}
}

export async function loadFontDynamicly(url: string) {
	const name = gen_id(8)
	const font = new FontFace(name, `url(${url})`, {})

	await font.load()

	console.log(font)

	document.fonts.add(font)

	return name
}
