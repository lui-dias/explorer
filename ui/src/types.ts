export type ExplorerItem = {
	name: string
	path: string
    kind: 'file' | 'folder'
    modified: string
	type: string
    size: number

    isEditMode: boolean
}

export type TSortTypes = 'name' | 'modified' | 'type' | 'size'