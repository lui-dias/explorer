export type ExplorerItem = {
	name: string
	path: string
	kind: 'file' | 'folder'
	modified: string
	type: string
	size: number
	parent: string

	isEditMode: boolean
	action?: 'create_file' | 'create_folder' | 'rename'
}

export type TSortTypes = 'name' | 'modified' | 'type' | 'size'
export type TFooter = {
	text: string
	type: 'info' | 'warning' | 'error' | 'none'
}
