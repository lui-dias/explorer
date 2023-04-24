import { writable } from 'svelte/store'
import type { ExplorerItem, TFooter, TSortTypes } from './types'

export const cwd = writable<string>('')
export const sortType = writable<TSortTypes>('name')
export const contextMenuOpen = writable<boolean>(false)
export const history = writable<string[]>([])
export const historyIndex = writable<number>(0)
export const selected = writable<ExplorerItem[]>([])
export const refreshExplorer = writable<() => Promise<void>>(async () => {})
export const explorerItems = writable<ExplorerItem[]>([])
export const isMultipleSelected = writable<boolean>(false)
export const scrollExplorerToEnd = writable<() => void>(() => {})
export const footer = writable<TFooter>({ text: '', type: 'none' })
export const settingsOpen = writable<boolean>(false)

export const settings = writable<{
    primaryColor: string
    textColor: string
}>({
    primaryColor: '#ddd6fe',
    textColor: '#f3e8ff'
})

export const cwdSplit = writable<string[]>([])
export const quickAccess = writable<ExplorerItem[]>([])
export const selectedQuickAccess = writable<ExplorerItem | null>(null)