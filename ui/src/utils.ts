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