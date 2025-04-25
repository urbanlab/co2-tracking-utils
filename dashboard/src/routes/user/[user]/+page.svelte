<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { writable } from 'svelte/store';
	import { on } from 'svelte/events';
	
    interface ListArray {
        Id: number;
        user: string;
        co2: number;
        date: string;
        type: string;
    }

	// Create tables store
	let tables = $state([]);
    const tableId = "mxmqg05jhqlquie"
	let currentUserTable = $state([]);
    let currentCo2 = $state(1);

	// Fetch tables function
	async function fetchTables(userId?: string) {
		if (!userId) {
			tables = [];
			return;
		}
		
		try {
			const response = await fetch(`/api/tables/chat?userId=${encodeURIComponent(userId)}`);
			
			if (!response.ok) {
				throw new Error('Failed to fetch tables');
			}
			
			const data = await response.json();
			tables = data;
			if (data.list) {
				currentUserTable = data.list;
			}
		} catch (error) {
			console.error('Error fetching tables:', error);
			tables = [];
			currentUserTable = [];
		}
	}
	
	// Watch tables function
	function watchTables(userId?: string) {
		console.log('watching tables', userId);
		fetchTables(userId);
		const intervalId = setInterval(() => fetchTables(userId), 10000);
		
		// Return cleanup function
		return () => clearInterval(intervalId);
	}
	
	// Load the table data when the component is mounted
	onMount(() => {
		const cleanup = watchTables($page.params.user);
		return cleanup;
	});

	let totalCo2 = $state({
		day: 0,
		week: 0,
		month: 0,
		total: 0,
		isactive: "total"
	});

	$effect(() => {
		if (!currentUserTable || currentUserTable.length === 0) {
            return;
        }
		
		// Reset totals
        let day = 0;
        let week = 0;
        let month = 0;
        let total = 0;
        
        // Get current date parts for comparison
        const now = new Date();
        const currentDate = now.toISOString().split('T')[0]; // YYYY-MM-DD
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth();
        const currentDay = now.getDate();
        
        // Calculate start of week (Sunday)
        const startOfWeek = new Date(now);
        startOfWeek.setDate(currentDay - now.getDay());
        const startOfWeekStr = startOfWeek.toISOString().split('T')[0];
        
        // Calculate start of month
        const startOfMonth = new Date(currentYear, currentMonth, 1);
        const startOfMonthStr = startOfMonth.toISOString().split('T')[0];
        
        console.log('currentUserTable', currentUserTable);
        currentUserTable.forEach((item: ListArray) => {
            const itemDate = item.date.split('T')[0]; // Ensure we get YYYY-MM-DD format
            
            // Check if the item is from today
            if (itemDate === currentDate) {
                day += item.co2;
            }
            
            // Check if the item is from this week
            if (itemDate >= startOfWeekStr) {
                week += item.co2;
            }
            
            // Check if the item is from this month
            if (itemDate >= startOfMonthStr) {
                month += item.co2;
            }
            
            // Add to total regardless of date
            total += item.co2;
        });
        
        totalCo2.day = day;
        totalCo2.week = week;
        totalCo2.month = month;
        totalCo2.total = total;
		currentCo2 = totalCo2.total;
	});

    $effect(() => {
        console.log('currentCo2', currentCo2);
    });
</script>

<section class="w-full flex flex-col justify-center items-center mt-14">
	<h1 class="w-1/3 text-3xl text-center font-bold mb-4">Ma consommation de CO2 sur le chat Erasme</h1>
	<div class="border rounded-xl w-1/3 p-4 border-red-300 flex justify-center flex-wrap">
		<div class={`stat ${totalCo2.isactive === 'day' ? 'stat-active' : ''}`} on:click={() => {
			currentCo2 = totalCo2.day;
			totalCo2.isactive = 'day';
		}}>
			<h3>Aujourd'hui</h3>
			<p>{totalCo2.day.toFixed(2)} g de CO2</p>
		</div>
		<div class={`stat ${totalCo2.isactive === 'week' ? 'stat-active' : ''}`} on:click={() => {
			currentCo2 = totalCo2.week;
			totalCo2.isactive = 'week';
		}}>
			<h3>Cette semaine</h3>
			<p>{totalCo2.week.toFixed(2)} g de CO2</p>
		</div>
		<div class={`stat ${totalCo2.isactive === 'month' ? 'stat-active' : ''}`} on:click={() => {
			currentCo2 = totalCo2.month;
			totalCo2.isactive = 'month';
		}}>
			<h3>Ce mois-ci</h3>
			<p>{totalCo2.month.toFixed(2)} g de CO2</p>
		</div>
		<div class={`stat w-full ${totalCo2.isactive === 'total' ? 'stat-active' : ''}`} on:click={() => {
			currentCo2 = totalCo2.total;
			totalCo2.isactive = 'total';
		}}>
			<h3>Total</h3>
			<p>{totalCo2.total.toFixed(2)} g de CO2</p>
		</div>
	</div>
    <div class="w-1/3">
        {#key currentCo2}
            <span class="hidden">{currentCo2.toFixed(2)/100}</span>
            <script name="impact-co2" src="https://impactco2.fr/iframe.js" data-type="comparateur" data-search={`?value=${currentCo2.toFixed(2)/100}&comparisons=email,rechercheweb,visioconference,biere,cafe,metro&language=fr&theme=default"`}></script>
        {/key}
    </div>
</section>