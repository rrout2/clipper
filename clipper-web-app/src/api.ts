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

export type FastpassInfo = {
    muniRidesTaken: number;
    bartRidesTaken: number;
    transfers: number;
    costWithoutFastpass: number;
};

export type IsWorthIt = {
    muniRidesTaken: number;
    bartRidesTaken: number;
    totalCost: number;
    muniOnlyFastpassWorthIt: boolean;
    muniBartFastpassWorthIt: boolean;
};

export type ClipperResponse = {
    transactions: Transaction[];
    fastpassInfo?: FastpassInfo;
    isWorthIt?: IsWorthIt;
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
        fastpassInfo: {
            muniRidesTaken: json.fastpass_info.muni_rides_taken,
            bartRidesTaken: json.fastpass_info.bart_rides_taken,
            transfers: json.fastpass_info.transfers,
            costWithoutFastpass: json.fastpass_info.cost_without_pass,
        },
        isWorthIt: {
            muniRidesTaken: json.is_worth_it.muni_rides_taken,
            bartRidesTaken: json.is_worth_it.bart_rides_taken,
            totalCost: json.is_worth_it.total_cost,
            muniOnlyFastpassWorthIt:
                json.is_worth_it.muni_only_fastpass_worth_it,
            muniBartFastpassWorthIt:
                json.is_worth_it.muni_bart_fastpass_worth_it,
        },
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
