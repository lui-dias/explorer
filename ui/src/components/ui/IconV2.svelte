<script lang="ts">
	import DOMPurify from 'dompurify'

	let svg = ''
	export let icon: string

	$: if (typeof window !== 'undefined') {
		async function main() {
			const r = await (await fetch(`http://localhost:3000/icons/${icon}.svg`)).text()

			svg = DOMPurify.sanitize(r)
		}

		main()
	}
</script>

<span class={$$props.class}>
	{@html svg}
</span>
