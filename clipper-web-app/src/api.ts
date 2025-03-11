export type Transaction = {
    balance: string;
    date: string;
    debit: string;
    location: string;
    product: string;
    route: string;
    transactionType: string;
    credit: string;
};

export type ClipperResponse = {
    transactions: Transaction[];
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function jsonToClipperResponse(json: any): ClipperResponse {
    return {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        transactions: json.transactions.map((t: any) => ({
            balance: t.BALANCE,
            date: t.DATE,
            debit: t.DEBIT,
            location: t.LOCATION,
            product: t.PRODUCT,
            route: t.ROUTE,
            transactionType: t.TRANSACTION_TYPE,
            credit: t.CREDIT,
        })),
    };
}

export async function parseFile(file: File, fastpass = false, worth = false) {
    const isLocal = window.location.hostname === "localhost";
    const apiUrl = isLocal
        ? "http://localhost:5000/api/"
        : "https://clipper-parser.onrender.com/api/";
    const formData = new FormData();
    formData.append("file", file);
    formData.append("fastpass", fastpass ? "true" : "false");
    formData.append("worth", worth ? "true" : "false");
    const res = await fetch(`${apiUrl}parse`, {
        method: "POST",
        body: formData,
    });
    const json = await res.json();
    return jsonToClipperResponse(json);
}

export async function healthCheck() {
    const isLocal = window.location.hostname === "localhost";
    const apiUrl = isLocal
        ? "http://localhost:5000/api/"
        : "https://clipper-parser.onrender.com/api/";
    return await fetch(`${apiUrl}health`);
}
