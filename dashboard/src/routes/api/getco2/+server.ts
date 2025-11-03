import { env } from "$env/dynamic/private";

const API_URL = env.PRIVATE_API_URL;

export const GET: RequestHandler = async ({ url }) => {
    const userId = url.searchParams.get('userid');
    console.log('userId:', userId);
    const co2 = {
        daily: 0,
        weekly: 0,
        monthly: 0,
        yearly: 0
    }
    // fetch daily CO2 data from the API
    try {
        const response = await fetch(`${API_URL}/api/v1/co2/user/${userId}?range=daily`);
        const data = await response.json();
        console.log("url:", `${API_URL}/api/v1/co2/user/${userId}?range=daily`);
        co2.daily = parseFloat(data.data.result[0].value[1]);
    } catch (error) {
        console.error('Error fetching CO2 data:', error);
    }
    // fetch weekly CO2 data from the API
    try {
        const response = await fetch(`${API_URL}/api/v1/co2/user/${userId}?range=weekly`);
        const data = await response.json();
        co2.weekly = parseFloat(data.data.result[0].value[1]);
    } catch (error) {
        console.error('Error fetching CO2 data:', error);
    }
    // fetch monthly CO2 data from the API
    try {
        const response = await fetch(`${API_URL}/api/v1/co2/user/${userId}?range=monthly`);
        const data = await response.json();
        co2.monthly = parseFloat(data.data.result[0].value[1]);
    } catch (error) {
        console.error('Error fetching CO2 data:', error);
    }
    // fetch yearly CO2 data from the API
    try {
        const response = await fetch(`${API_URL}/api/v1/co2/user/${userId}?range=yearly`);
        const data = await response.json();
        co2.yearly = parseFloat(data.data.result[0].value[1]);
    } catch (error) {
        console.error('Error fetching CO2 data:', error);
    }
    return new Response(JSON.stringify(co2), {
        headers: { 'Content-Type': 'application/json' }
    });
};