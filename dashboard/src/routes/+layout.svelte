<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import { tables, watchTables } from '$lib/stores/tables';
	let { children } = $props();
	// Load the table data when the component is mounted
	onMount( async () => {
		//await watchTables();
	});
	
</script>
<div class="flex w-full">
	{@render children()}
</div>
