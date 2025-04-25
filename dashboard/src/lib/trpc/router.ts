import type { Context } from '$lib/trpc/context';
import { initTRPC } from '@trpc/server';
import { env } from "$env/dynamic/private";
import { z } from 'zod'; // You'll need to import zod for input validation

export const t = initTRPC.context<Context>().create();

const nocodb = {
    url: env.PRIVATE_NOCODB_URL,
    token: env.PRIVATE_NOCODB_API_TOKEN,
};

console.log(nocodb)
export const router = t.router({
    greeting: t.procedure.query(async () => {
        return `Hello tRPC v10 @ ${new Date().toLocaleTimeString()}`;
    }),
    // get table by id with optional userId filter
    getTableById: t.procedure
        .input(z.object({ 
            tableId: z.string(),
            where: z.string().optional() 
        }))
        .query(async ({ input }) => {
            try {
                // Build the URL with optional where parameter
                let url = `${nocodb.url}/api/v2/tables/${input.tableId}/records`;
                
                // Add the where query parameter if provided
                if (input.where) {
                    url += `?${input.where}`;
                }
                
                const response = await fetch(url, {
                    headers: {
                        'xc-token': nocodb.token,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch table: ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('Fetched data:', data);
                return data;
            } catch (error) {
                console.error('Error fetching table:', error);
                throw error;
            }
        }),
});

export const createCaller = t.createCallerFactory(router);

export type Router = typeof router;