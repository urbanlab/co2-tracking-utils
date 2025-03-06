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
    // get table by id
    getTableById: t.procedure
        .input(z.object({ tableId: z.string() }))
        .query(async ({ input }) => {
            try {
                const response = await fetch(`${nocodb.url}/api/v2/tables/${input.tableId}/records`, {
                    headers: {
                        'xc-token': nocodb.token,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch table: ${response.statusText}`);
                }
                
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error fetching table:', error);
                throw error;
            }
        }),
});

export const createCaller = t.createCallerFactory(router);

export type Router = typeof router;