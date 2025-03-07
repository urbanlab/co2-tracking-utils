<script lang="ts">
    import { page } from '$app/state';
    import { tables } from '$lib/stores/tables';
    import type { Table, Row, TableRecord } from '$lib/types';
    import { Chart, registerables } from 'chart.js';
    import { onMount } from 'svelte';

    // Register all Chart.js components
    Chart.register(...registerables);

    let tableName = $state(page.params.name);
    let table: TableRecord;
    let chartHtmlElement: HTMLCanvasElement;
    let chart: Chart;

    let filter: "day" | "week" | "month" | "year" = "week"; // Default to week

    // Group data by week and calculate totals
    function getWeeklyCO2Data(rows: Row[]) {
        const weekMap = new Map();
        
        // Sort the rows by date
        const sortedRows = [...rows].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        
        sortedRows.forEach(row => {
            const date = new Date(row.date);
            // Get the start of the week (Sunday)
            const startOfWeek = new Date(date);
            startOfWeek.setDate(date.getDate() - date.getDay());
            const weekKey = startOfWeek.toISOString().substring(0, 10);
            
            if (!weekMap.has(weekKey)) {
                weekMap.set(weekKey, 0);
            }
            
            weekMap.set(weekKey, weekMap.get(weekKey) + row.co2);
        });
        
        // Convert to arrays for Chart.js
        const labels = Array.from(weekMap.keys()).map(date => {
            const weekStart = new Date(date);
            const weekEnd = new Date(weekStart);
            weekEnd.setDate(weekStart.getDate() + 6);
            return `${weekStart.toLocaleDateString()} - ${weekEnd.toLocaleDateString()}`;
        });
        
        const data = Array.from(weekMap.values());
        
        return { labels, data };
    }

    function updateChart() {
        if (table && table.data && table.data.list) {
            let labels = [];
            let data = [];

            if (filter === "week") {
                const weeklyData = getWeeklyCO2Data(table.data.list);
                labels = weeklyData.labels;
                data = weeklyData.data;
            }
            // Add other filters as needed: day, month, year

            if (chart) {
                chart.destroy();
            }

            chart = new Chart(chartHtmlElement, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'CO2 Consumption',
                        data: data,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'CO2 (units)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Week'
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Weekly CO2 Consumption'
                        }
                    }
                }
            });
        }
    }

    $effect(() => {
        tableName = page.params.name;
        console.log('tableName', tableName);
        table = $tables.find(t => t.name === tableName);
        console.log('table', table);
        
        // Update the chart whenever the table or filter changes
        if (chartHtmlElement) {
            updateChart();
        }
    });

    $effect(() => {
        // Update chart when filter changes
        if (chartHtmlElement && table) {
            updateChart();
        }
    });

    onMount(() => {
        console.log('onMount');
        if (table && table.data) {
            updateChart();
        }
    });
</script>

<section>
    {#if !table}
        <p>Loading...</p>
    {:else}
        <h1>{table.name}</h1>
        <p>Filter: {filter}</p>
        <div class="filter-buttons">
            <button class:active={filter === 'day'} on:click={() => filter = 'day'}>Day</button>
            <button class:active={filter === 'week'} on:click={() => filter = 'week'}>Week</button>
            <button class:active={filter === 'month'} on:click={() => filter = 'month'}>Month</button>
            <button class:active={filter === 'year'} on:click={() => filter = 'year'}>Year</button>
        </div>
    {/if}
    <div class="chart-container">
        <canvas bind:this={chartHtmlElement}></canvas>
    </div>
</section>

<style>
    .chart-container {
        width: 100%;
        height: 400px;
        margin-top: 20px;
    }
    
    .filter-buttons {
        margin: 15px 0;
    }
    
    button {
        margin-right: 8px;
        padding: 6px 12px;
        border: 1px solid #ccc;
        background-color: #f8f8f8;
        border-radius: 4px;
        cursor: pointer;
    }
    
    button.active {
        background-color: #007bff;
        color: white;
        border-color: #0069d9;
    }
</style>