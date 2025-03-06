import { writable } from "svelte/store";
import { trpc } from '$lib/trpc/client';
import { env } from "$env/dynamic/public";
import type { TableRecord } from "$lib/types";
 
export const tables = writable<TableRecord[]>([]);
const tablesId: Array<string> = env.PUBLIC_NOCODB_TABLES_ID.split(",");
const tablesName: Array<string> = env.PUBLIC_NOCODB_TABLES_NAME.split(",");
console.log(tablesId);

export async function fetchTables() {

    const tableData = await Promise.all(tablesId.map(async (tableId) => {
        return trpc().getTableById.query({ tableId });
    }));

    tables.set(tableData.map((data, index) => {
        return {
            name: tablesName[index],
            data
        };
    }));

}

export async function watchTables() {
    console.log('watching tables');
    fetchTables();
    setInterval(fetchTables, 10000);
}