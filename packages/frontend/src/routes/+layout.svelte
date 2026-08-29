<script lang="ts">
	import '../app.css';
	import { session } from '$lib/stores/session.svelte';
	import Topbar from '$lib/components/Topbar.svelte';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		session.load();
		session.applyTheme();
	});
</script>

<Topbar />

{@render children()}
