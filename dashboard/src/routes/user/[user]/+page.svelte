<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { writable } from 'svelte/store';
	import { on } from 'svelte/events';


	let totalCo2 = $state({
		daily: 0,
		weekly: 0,
		monthly: 0,
		yearly: 0,
		isactive: 'yearly',
	});
	let currentCo2 = $state(1);

	// Fetch tables function
	async function fetchCo2(userId?: string) {
		if (!userId) {
			return;
		}

		try {
			const response = await fetch(`/api/getco2?userid=${userId}`);
			totalCo2 = await response.json();
		}
		catch (error) {
			console.error('Error fetching CO2 data:', error);
		}
	}
	// Load the table data when the component is mounted
	onMount(async () => {
		await fetchCo2($page.params.user);
		currentCo2 = totalCo2.yearly;
	});


	
</script>

<section class="mt-14 flex w-full flex-col items-center justify-center">
	<h1 class="mb-4 w-1/3 text-center text-3xl font-bold">
		Ma consommation de CO2 sur le chat Erasme
	</h1>
	<div class="flex w-1/3 flex-wrap justify-center rounded-xl border border-red-300 p-4">
		<div
			class={`stat ${totalCo2.isactive === 'day' ? 'stat-active' : ''}`}
			on:click={() => {
				currentCo2 = totalCo2.daily;
				totalCo2.isactive = 'daily';
			}}
		>
			<h3>Aujourd'hui</h3>
			<p>{totalCo2.daily.toFixed(2)} g de CO2</p>
		</div>
		<div
			class={`stat ${totalCo2.isactive === 'weekly' ? 'stat-active' : ''}`}
			on:click={() => {
				currentCo2 = totalCo2.weekly;
				totalCo2.isactive = 'weekly';
			}}
		>
			<h3>Cette semaine</h3>
			<p>{totalCo2.weekly.toFixed(2)} g de CO2</p>
		</div>
		<div
			class={`stat ${totalCo2.isactive === 'monthly' ? 'stat-active' : ''}`}
			on:click={() => {
				currentCo2 = totalCo2.monthly;
				totalCo2.isactive = 'monthly';
			}}
		>
			<h3>Ce mois-ci</h3>
			<p>{totalCo2.monthly.toFixed(2)} g de CO2</p>
		</div>
		<div
			class={`stat w-full ${totalCo2.isactive === 'yearly' ? 'stat-active' : ''}`}
			on:click={() => {
				currentCo2 = totalCo2.yearly;
				totalCo2.isactive = 'yearly';
			}}
		>
			<h3>Année</h3>
			<p>{totalCo2.yearly.toFixed(2)} g de CO2</p>
		</div>
	</div>
	<div class="w-1/3">
		{#key currentCo2}
			<span class="hidden">{currentCo2.toFixed(2) / 1000}</span>
			<script
				name="impact-co2"
				src="https://impactco2.fr/iframe.js"
				data-type="comparateur"
				data-search={`?value=${currentCo2.toFixed(2) / 1000}&comparisons=email,rechercheweb,visioconference,biere,cafe,metro&language=fr&theme=default"`}
			></script>
		{/key}
	</div>
	<div
		class=" mt-8 mb-4 flex w-1/3 flex-wrap justify-center rounded-xl border border-red-300 p-4 italic"
	>
		<p>
			Le calcul est basé sur la puissance de la carte graphique (500W/h) x la durée de calcul de la
			réponse du chat (x secondes) x le facteur d'émission co2 moyen en france (50g/kwh)
		</p>
	</div>
</section>

