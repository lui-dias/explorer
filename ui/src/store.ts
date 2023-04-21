import { writable } from 'svelte/store'
import type { ExplorerItem, TSortTypes } from './types'

export const cwd = writable<string>('')
export const sortType = writable<TSortTypes>('name')
export const contextMenuOpen = writable<boolean>(false)
export const history = writable<string[]>([])
export const historyIndex = writable<number>(0)
export const selectedItem = writable<ExplorerItem | null>(null)
export const refreshExplorer = writable<() => Promise<void>>(async () => {})
export const explorerItems = writable<ExplorerItem[]>([])

export const footer = writable<{
	text: string
	type: 'info' | 'warning' | 'error' | 'none'
}>({ text: '', type: 'none' })
