<script lang="ts">
	import ArrowLeft from '../icons/ArrowLeft.svelte'
	import Chevron from '../icons/Chevron.svelte'
	import Copy from '../icons/Copy.svelte'
	import Disk from '../icons/Disk.svelte'
	import Info from '../icons/Info.svelte'
	import Preview from '../icons/Preview.svelte'
	import Search from '../icons/Search.svelte'
	import Usb from '../icons/Usb.svelte'
	import Abc from '../icons/contextmenu/Abc.svelte'
	import Asc from '../icons/contextmenu/Asc.svelte'
	import Calendar from '../icons/contextmenu/Calendar.svelte'
	import Desc from '../icons/contextmenu/Desc.svelte'
	import NewFile from '../icons/contextmenu/NewFile.svelte'
	import NewFolder from '../icons/contextmenu/NewFolder.svelte'
	import Pin from '../icons/contextmenu/Pin.svelte'
	import Plus from '../icons/contextmenu/Plus.svelte'
	import Size from '../icons/contextmenu/Size.svelte'
	import Sort from '../icons/contextmenu/Sort.svelte'
	import Types from '../icons/contextmenu/Types.svelte'
	import Unpin from '../icons/contextmenu/Unpin.svelte'
	import Vscode from '../icons/contextmenu/Vscode.svelte'

	import { tv } from 'tailwind-variants'

	const _icon = tv({
		variants: {
			glow: {
				true: 'drop-shadow-[0_0_5px_var(--primary)]',
				false: '',
			},
			colored: {
				true: 'fill-primary group-disabled:fill-gray-400 group-disabled:drop-shadow-none',
				false: '',
			},
            stroked: {
                true: 'stroke-primary group-disabled:stroke-gray-400 group-disabled:drop-shadow-none',
                false: '',
            }
		},
	})

	export let glow = false
	export let colored = false
    export let stroked = false
	export let icon: string

	// prettier-ignore
	const icons = {
        'OtherNewFile'             : NewFile,
        'OtherArrowLeft'           : ArrowLeft,
        'OtherSort'                : Sort,
        'OtherPlus'                : Plus,
        'OtherNewFolder'           : NewFolder,
        'OtherAbc'                 : Abc,
        'OtherCalendar'            : Calendar,
        'OtherSize'                : Size,
        'OtherTypes'               : Types,
        'OtherPin'                 : Pin,
        'OtherUnpin'               : Unpin,
        'OtherSearch'              : Search,
        'OtherDisk'                : Disk,
        'OtherChevron'             : Chevron,
        'OtherAsc'                 : Asc,
        'OtherDesc'                : Desc,
        'OtherUsb'                 : Usb,
        'OtherInfo'                : Info,
        'OtherCopy'                : Copy,
        'OtherVscode'              : Vscode,
        'OtherPreview'             : Preview,
	} as Record<string, any>
</script>

<svelte:component this={icons[icon]} class={`${_icon({ glow, colored, stroked })} ${$$props.class}`} />
