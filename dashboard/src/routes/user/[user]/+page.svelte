<script lang="ts">
	import { onMount } from 'svelte';
    import { page } from '$app/state';
	import { tables, watchTables } from '$lib/stores/tables';
	// Load the table data when the component is mounted
	onMount( async () => {
		await watchTables();
	});

	let curentUserTable = []
	let totalCo2 = {
		day: 0,
		week: 0,
		month: 0,
		total: 0
	}

	$effect(() => {
		if (!$tables[0]?.data) return;
		console.log($tables)
		// filter tables.[0].data.list.user == page.params.name
		curentUserTable = $tables[0].data.list.filter((item) => item.user == page.params.user)
		console.log(curentUserTable)

		const today = new Date()
		totalCo2 = { day: 0, week: 0, month: 0, total: 0 };
		curentUserTable.forEach((item) => {
            const date = new Date(item.date);
			console.log(date.getDate())
			console.log(today.getDate())
            
            // Daily CO2 (only today)
            if (
                date.getDate() === today.getDate() &&
                date.getMonth() === today.getMonth() &&
                date.getFullYear() === today.getFullYear()
            ) {
                totalCo2.day += item.co2;
            }

            // Weekly CO2 (last 7 days)
            const oneWeekAgo = new Date();
            oneWeekAgo.setDate(today.getDate() - 7);
            if (date >= oneWeekAgo && date <= today) {
                totalCo2.week += item.co2;
            }

            // Monthly CO2 (same month and year)
            if (
                date.getMonth() === today.getMonth() &&
                date.getFullYear() === today.getFullYear()
            ) {
                totalCo2.month += item.co2;
            }

            // Total CO2
            totalCo2.total += item.co2;
			console.log(totalCo2)
        });
	})
    
</script>
<section>

</section>