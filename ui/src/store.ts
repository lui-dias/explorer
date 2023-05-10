import { writable } from 'svelte/store'
import type { TConfig, ExplorerItem, TFooter, TSortTypes, TDisksInfo } from './types'

export const cwd = writable<string>('')
export const sortType = writable<TSortTypes>('name')
export const sortTypeReversed = writable<boolean>(false)
export const contextMenuOpen = writable<boolean>(false)
export const history = writable<string[]>([])
export const historyIndex = writable<number>(0)
export const selected = writable<ExplorerItem[]>([])
export const explorerItems = writable<ExplorerItem[]>([])
export const isMultipleSelected = writable<boolean>(false)
export const scrollExplorerToEnd = writable<() => void>(() => {})
export const footer = writable<TFooter>({ text: '', type: 'none' })
export const settingsOpen = writable<boolean>(false)

export const settings = writable<TConfig>({} as TConfig)

export const cwdSplit = writable<string[]>([])
export const quickAccess = writable<ExplorerItem[]>([])
export const selectedQuickAccess = writable<ExplorerItem | null>(null)

export const searchItems = writable<ExplorerItem[]>([])
export const isSearching = writable<boolean>(true)

export const disks = writable<TDisksInfo[]>([])