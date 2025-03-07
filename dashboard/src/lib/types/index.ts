export interface Table {
    list: Row[];
}


export interface Row {
    id: string;
    user?: string;
    co2: number;
    date: string;
}

export interface TableRecord {
    name: string;
    data: {
        list: Row[];
    }
}