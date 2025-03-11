import { useEffect, useState } from "react";
import "./App.css";
import { parseFile, Transaction } from "./api";

function App() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [transactions, setTransactions] = useState<Transaction[]>([]);

    useEffect(() => {
        if (!selectedFile) {
            return;
        }
        parseFile(selectedFile)
            .then((res) => setTransactions(res.transactions))
            .catch((err) => {
                console.error(err);
                setTransactions([]);
            });
    }, [selectedFile]);
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const fileList = event.target.files;
        if (!fileList || fileList.length === 0) {
            return;
        }
        setSelectedFile(fileList[0]);
    };
    return (
        <>
            <input type="file" accept=".pdf" onChange={handleFileChange} />
            {selectedFile && <p>Selected file: {selectedFile.name}</p>}
            {transactions.length > 0 && (
                <>{transactions.length} transactions found</>
            )}
        </>
    );
}
export default App;
