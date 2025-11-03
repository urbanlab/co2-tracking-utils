<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	let { children } = $props();
	// Load the table data when the component is mounted
	onMount( async () => {
		//await watchTables();
	});
	
</script>
<div class="flex w-full">
	{@render children()}
</div>
