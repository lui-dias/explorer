import type { ExplorerItem } from './types'

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

export function isPathChild(parent: string, child: string) {
	return child.startsWith(parent) && child !== parent
}

export function formatBytes(bytes: number) {
	if (bytes < 1024) {
		return `${bytes} B`
	}

	if (bytes < 1024 ** 2) {
		return `${(bytes / 1024).toFixed(2)} KB`
	}

	if (bytes < 1024 ** 3) {
		return `${(bytes / 1024 ** 2).toFixed(2)} MB`
	}

	if (bytes < 1024 ** 4) {
		return `${(bytes / 1024 ** 3).toFixed(2)} GB`
	}

	return `${(bytes / 1024 ** 4).toFixed(2)} TB`
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
	ls: async (folder: string): Promise<ExplorerItem[]> => {
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
		path: string,
		moveToTrash: boolean,
	): Promise<{
		end: boolean
		total: number
		deleted: number
	}> => {
		// @ts-ignore
		return await pywebview.api.stream_delete(path, moveToTrash)
	},
	reset_stream_size: async (path: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.reset_stream_size(path)
	},
	reset_stream_delete: async (path: string): Promise<void> => {
		// @ts-ignore
		return await pywebview.api.reset_stream_delete(path)
	},
}

export function isClient() {
	return typeof window !== 'undefined'
}
