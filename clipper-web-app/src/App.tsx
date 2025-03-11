import { useEffect, useState } from "react";
import "./App.css";
import {
    FastpassInfo,
    healthCheck,
    IsWorthIt,
    parseFile,
    Transaction,
} from "./api";
import { Button, CircularProgress } from "@mui/material";

function App() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [fastpassInfo, setFastpassInfo] = useState<
        FastpassInfo | undefined
    >();
    const [isWorthIt, setIsWorthIt] = useState<IsWorthIt | undefined>();
    const [healthy, setHealthy] = useState<boolean>(false);

    useEffect(() => {
        if (!selectedFile) {
            return;
        }
        parseFile(selectedFile, true, true)
            .then((res) => {
                setTransactions(res.transactions);
                setFastpassInfo(res.fastpassInfo);
                setIsWorthIt(res.isWorthIt);
            })
            .catch((err) => {
                console.error(err);
                setTransactions([]);
            });
    }, [selectedFile]);
    useEffect(() => {
        healthCheck()
            .then(() => {
                setHealthy(true);
            })
            .catch((err) => {
                console.error(err);
                setHealthy(false);
            });
    }, []);
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedFile(null);
        setTransactions([]);
        const fileList = event.target.files;
        if (!fileList || fileList.length === 0) {
            return;
        }
        setSelectedFile(fileList[0]);
    };
    return (
        <>
            {!healthy && <CircularProgress />}
            {healthy && (
                <>
                    <Button variant="contained" component="label">
                        Upload Clipper PDF
                        <input
                            type="file"
                            accept=".pdf"
                            onChange={handleFileChange}
                            hidden
                        />
                    </Button>
                    {selectedFile && <p>Selected file: {selectedFile.name}</p>}
                    {selectedFile && transactions.length === 0 && (
                        <CircularProgress />
                    )}
                    {transactions.length > 0 && (
                        <>{transactions.length} transactions found</>
                    )}
                    {fastpassInfo && (
                        <>
                            <p>
                                Fastpass Info:{" "}
                                {JSON.stringify(fastpassInfo, null, 2)}
                            </p>
                        </>
                    )}
                    {isWorthIt && (
                        <>
                            <p>
                                Is Worth It:{" "}
                                {JSON.stringify(isWorthIt, null, 2)}
                            </p>
                        </>
                    )}
                </>
            )}
        </>
    );
}
export default App;
