<script lang="ts">
    import { page } from '$app/state';
	import { tables } from '$lib/stores/tables';
	import type { Table } from '$lib/types';
    import { Chart } from 'chart.js';
	import { onMount } from 'svelte';

    let tableName = $state(page.params.name);
    let table: Table;
    let chartHtmlElement: HTMLCanvasElement;

    let filter: "day" | "week" | "month" | "year" = "day";

    $effect(() => {
        tableName = page.params.name;
        console.log('tableName', tableName);
        table = $tables.find(t => t.name === tableName) || { name: 'Table not found' };
        console.log('table', table);

    });

    onMount(() => {
        console.log('onMount');
        new Chart(chartHtmlElement, {
            type: 'bar',
            data: {
            labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
            datasets: [{
                label: '# of Votes',
                data: [12, 19, 3, 5, 2, 3],
                borderWidth: 1
            }]
            },
            options: {
            scales: {
                y: {
                beginAtZero: true
                }
            }
            }
        });
    });



    



</script>
<section>
    {#if !table}
        <p>Loading...</p>
    {:else}
        <h1>{table.name}</h1>
        <p>Filter: {filter}</p>
        <button on:click={() => filter = 'day'}>Day</button>
        <button on:click={() => filter = 'week'}>Week</button>
        <button on:click={() => filter = 'month'}>Month</button>
        <button on:click={() => filter = 'year'}>Year</button>

        <div>
            <canvas bind:this={chartHtmlElement}></canvas>
        </div>
    {/if}
</section>