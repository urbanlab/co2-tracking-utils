import { json } from '@sveltejs/kit';
import { env } from "$env/dynamic/private";

const nocodb = {
    url: env.PRIVATE_NOCODB_URL,
    token: env.PRIVATE_NOCODB_API_TOKEN,
};

export const GET: RequestHandler = async ({ url }) => {
    const tableId = "mxmqg05jhqlquie"
    const userId = url.searchParams.get('userId');
    console.log('tableId:', tableId);
    console.log('userId:', userId);
    if (!tableId) {
        return json({ error: 'tableId is required' }, { status: 400 });
    }
    
    if (!userId) {
        return json({ error: 'userId is required' }, { status: 400 });
    }
    
    try {
        const whereClause = `where=(user,eq,${userId})`;
        console.log('whereClause:', whereClause);
        const apiUrl = `${nocodb.url}/api/v2/tables/${tableId}/records?${whereClause}&limit=1000`;
        
        const response = await fetch(apiUrl, {
            headers: {
                'xc-token': nocodb.token,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Failed to fetch table: ${response.statusText}`);
        }
        
        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error fetching table:', error);
        return json({ error: 'Failed to fetch table' }, { status: 500 });
    }
};