import { get } from 'svelte/store'
import { E } from './event'
import { cwd, cwdSplit, history, historyIndex, isLoading, sortType, ws } from './store'
import type { ExplorerItem, TConfig, TDisksInfo, TInstalledApp } from './types'

// https://stackoverflow.com/a/3028037
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

// Sort array by key, like python sorted function
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

export const py = {
	close: async (): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('close')
	},
	minimize: async (): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('minimize')
	},
	maximize: async (): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('maximize')
	},
	startLs: async (folder: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('start_ls', folder)
	},
	startFind: async (path: string, query: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('start_find', path, query)
	},
	startFolderSize: async (path: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('start_folder_size', path)
	},
	startDelete: async (
		id: string,
		path: string | string[],
		moveToTrash: boolean,
	): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('start_delete', id, path, moveToTrash)
	},
	ls: async (
		folder: string,
	): Promise<{
		items: ExplorerItem[]
		end: boolean
	}> => {
		// @ts-ignore
		return await callWsFunction('ls', folder)
	},
	home: async (): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('home')
	},
	rename: async (from: string, to: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('rename', from, to)
	},
	createFile: async (path: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('create_folder', path)
	},
	createFolder: async (path: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('create_folder', path)
	},
	exists: async (path: string): Promise<boolean> => {
		// @ts-ignore
		return await callWsFunction('exists', path)
	},
	streamFolderSize: async (
		path: string,
	): Promise<{
		size: number
		end: boolean
	}> => {
		// @ts-ignore
		return await callWsFunction('stream_folder_size', path)
	},
	streamDelete: async (
		id: string,
	): Promise<{
		end: boolean
		total: number
		deleted: number
		last_deleted: string
	}> => {
		// @ts-ignore
		return await callWsFunction('stream_delete', id)
	},

	streamFind: async (
		path: string,
	): Promise<{
		end: boolean
		total: number
		files: ExplorerItem[]
	}> => {
		// @ts-ignore
		return await callWsFunction('stream_find', path)
	},

	deleteAllStreamsLs: async () => {
		// @ts-ignore
		return await callWsFunction('delete_all_streams_ls')
	},

	deleteAllStreamsFind: async () => {
		// @ts-ignore
		return await callWsFunction('delete_all_streams_find')
	},

	deleteAllStreamsFolderSize: async () => {
		// @ts-ignore
		return await callWsFunction('delete_all_streams_folder_size')
	},

	deleteAllStreamsDelete: async () => {
		// @ts-ignore
		return await callWsFunction('delete_all_streams_delete')
	},

	getPathInfo: async (path: string): Promise<ExplorerItem> => {
		// @ts-ignore
		return await callWsFunction('get_path_info', path)
	},

	getConfig: async (): Promise<TConfig> => {
		// @ts-ignore
		return await callWsFunction('get_config')
	},

	setConfig: async (config: TConfig): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('set_config', config)
	},

	read: async (path: string): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('read', path)
	},
	readB64: async (path: string): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('read_b64', path)
	},
	user: async () => {
		// @ts-ignore
		return await callWsFunction('user')
	},
	pwd: async () => {
		// @ts-ignore
		return await callWsFunction('pwd')
	},
	setupTests: async () => {
		// @ts-ignore
		return await callWsFunction('setup_tests')
	},
	clearTests: async () => {
		// @ts-ignore
		return await callWsFunction('clear_tests')
	},
	disksInfo: async (): Promise<TDisksInfo[]> => {
		// @ts-ignore
		return await callWsFunction('disks_info')
	},
	get: async (key: string): Promise<any> => {
		// @ts-ignore
		return await callWsFunction('get', key)
	},
	set: async (key: string, value: any): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('set', key, value)
	},
	getFontWeight: async (path: string): Promise<number | null> => {
		// @ts-ignore
		return await callWsFunction('get_font_weight', path)
	},
	copy: async (path: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('copy', path)
	},
	paste: async (folder: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('paste', folder)
	},
	crc32: async (path: string): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('get_crc32', path)
	},
	md5: async (path: string): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('get_md5', path)
	},
	sha1: async (path: string): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('get_sha1', path)
	},
	sha256: async (path: string): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('get_sha256', path)
	},
	getInstalledApps: async (): Promise<TInstalledApp[]> => {
		// @ts-ignore
		return await callWsFunction('get_installed_apps')
	},
	shell: async (command: string): Promise<void> => {
		// @ts-ignore
		return await callWsFunction('shell', command)
	},
	parse_path: async (path: string): Promise<string> => {
		// @ts-ignore
		return await callWsFunction('parse_path', path)
	},
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

// ? If is the last path in history, append new path
// path = '/home/user/Downloads'
//
// history = ['/home', '/home/user']
//              v
//              v
// history = ['/home', '/home/user', '/home/user/Downloads']
//
// ? else remove all paths after history[hi + 1], then append new path
//
// path = '/home/user/Downloads'
// historyIndex = 1
//
// history = ['/home', '/home/user', '/home/user/Videos', '/home/user/Videos/House']
//              v
//              v
// history = ['/home', '/home/user', '/home/user/Downloads']

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

// ? Remove all paths, then split path folders
//
// path = /home/user/Downloads
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
		return sort(items, i => i.name)
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

export function assert(condition: boolean, message: string) {
	if (!condition) {
		throw new Error(message)
	}
}

export async function loadFontDynamically(url: string) {
	const name = gen_id(8)
	const font = new FontFace(name, `url(${url})`)

	await font.load()

	document.fonts.add(font)

	return name
}

export function waitWsOpen() {
	return new Promise<void>(async (resolve, reject) => {
		const $ws = get(ws)

		$ws.addEventListener('open', () => {
			resolve()
		})
	})
}

export function waitAppLoad() {
	return new Promise<void>(async (resolve, reject) => {
		isLoading.subscribe(v => {
			if (!v) resolve()
		})
	})
}

export function callWsFunction(name: string, ...args: any[]) {
	const $ws = get(ws)

	return new Promise((resolve, reject) => {
		const response_id = gen_id(8)

		function listener(event: MessageEvent) {
			const { type, id, r } = JSON.parse(event.data) as {
				type: 'return'
				id: string
				r: any
			}

			if (type === 'return' && id === response_id) {
				$ws.removeEventListener('message', listener)
				resolve(r)
			}
		}

		$ws.addEventListener('message', listener)
		$ws.send(JSON.stringify({ type: 'call', id: response_id, name, args }))
	})
}

export function createWs() {
	const _ws = new WebSocket('ws://localhost:3004')

	_ws.onclose = createWs

	ws.set(_ws)
}

export function xIsWhatPercentOfY(x: number, y: number) {
	return (x / y) * 100
}

export async function clipboard(text: string) {
	await navigator.clipboard.writeText(text)

	await E.footerText({
		text: `Copied to clipboard: ${text}`,
		type: 'info',
	})
}
