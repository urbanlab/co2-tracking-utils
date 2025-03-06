<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import { tables, watchTables } from '$lib/stores/tables';
	let { children } = $props();
	// Load the table data when the component is mounted
	onMount( async () => {
		await watchTables();
	});
	
</script>
<div class="flex">
	<nav class="w-1/5">
		<ul>
			{#if $tables}
				{#each $tables as table}
					<li><a href="/table/{table.name}">{table.name}</a></li>
				{/each}
			{/if}
		</ul>
	</nav>
	{@render children()}
</div>
