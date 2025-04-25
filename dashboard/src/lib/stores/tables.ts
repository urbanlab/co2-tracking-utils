import { writable } from "svelte/store";
import { trpc } from '$lib/trpc/client';
import { env } from "$env/dynamic/public";
import type { TableRecord } from "$lib/types";
 
export const tables = writable<TableRecord[]>([]);
const tablesId: Array<string> = env.PUBLIC_NOCODB_TABLES_ID.split(",");
const tablesName: Array<string> = env.PUBLIC_NOCODB_TABLES_NAME.split(",");
console.log(tablesId);

// Function to build the where clause for sorting by user id
function buildWhereClause(userId: string): string {
 return `where=(user,eq,"${userId}")`;
}

export async function fetchTables(userId?: string) {
  const tableData = await Promise.all(tablesId.map(async (tableId) => {
    let queryOptions = { tableId };
    if (userId) {
      console.log('fetching tables for userId', userId);
      queryOptions = { ...queryOptions, where: buildWhereClause(userId) };
    }
    console.log('queryOptions', queryOptions);
    return trpc().getTableById.query(queryOptions);
  }));
  tables.set(tableData.map((data, index) => {
    return {
      name: tablesName[index],
      data
    };
  }));
}

export async function watchTables(userId?: string) {
  console.log('watching tables', userId);
  fetchTables(userId);
  const intervalId = setInterval(() => fetchTables(userId), 10000);

  // Return the interval ID so it can be cleared if needed
  return intervalId;
}