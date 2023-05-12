export type ExplorerItem = {
	name: string
	path: string
	kind: 'file' | 'folder'
	modified: string
    accessed: string
    created: string
	type: string
	size: number
	parent: string

	isEditMode: boolean
	action?: 'createFile' | 'createFolder' | 'rename'
}

export type TSortTypes = 'name' | 'modified' | 'type' | 'size'
export type TFooter = {
	text: string
	type: 'info' | 'warning' | 'error' | 'none'
}

export type TConfig = {
	colors: {
		primary: string
		accent: string
		text: string
		background: string
		divider: string
	}
}

export type TDisksInfo = {
    name: string
    device: string
    path: string
    total: number
    used: number
    free: number
    percent: number
}