import { useEffect, useState } from "react";
import styles from "./App.module.css";
import {
    FastpassInfo,
    healthCheck,
    IsWorthIt,
    parseFile,
    Transaction,
} from "./api";
import {
    Button,
    CircularProgress,
    FormControlLabel,
    IconButton,
    Switch,
    Tooltip,
} from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
function App() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [fastpassInfo, setFastpassInfo] = useState<
        FastpassInfo | undefined
    >();
    const [isWorthIt, setIsWorthIt] = useState<IsWorthIt | undefined>();
    const [haveFastpass, setHaveFastpass] = useState<boolean>(false);
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
    function downloadJSON(): void {
        if (transactions.length === 0 || !selectedFile) {
            console.warn("No transactions to download");
            return;
        }

        const blob = new Blob([JSON.stringify(transactions, null, 2)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute(
            "download",
            `${selectedFile.name.split(".pdf")[0]}.json`
        );
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    return (
        <div className={styles.root}>
            {!healthy && (
                <div className={styles.container}>
                    <CircularProgress />
                    It may take a minute or two load at first, thanks for your
                    patience!
                </div>
            )}
            {healthy && (
                <div className={styles.container}>
                    <FormControlLabel
                        label="Have Fastpass?"
                        control={
                            <Switch
                                checked={haveFastpass}
                                onChange={() => setHaveFastpass(!haveFastpass)}
                            />
                        }
                    />
                    <Button variant="contained" component="label">
                        Upload Clipper PDF
                        <input
                            type="file"
                            accept=".pdf"
                            onChange={handleFileChange}
                            hidden
                        />
                    </Button>
                    {!selectedFile && (
                        <Tooltip title="Where to find your Clipper PDF">
                            <IconButton
                                onClick={() =>
                                    window.open(
                                        "https://github.com/rrout2/clipper?tab=readme-ov-file#where-to-find-ride-history"
                                    )
                                }
                            >
                                <HelpOutlineIcon />
                            </IconButton>
                        </Tooltip>
                    )}
                    {selectedFile && (
                        <div>Selected file: {selectedFile.name}</div>
                    )}
                    {selectedFile && (
                        <Button onClick={downloadJSON} variant="outlined">
                            Download JSON
                        </Button>
                    )}
                    {selectedFile && transactions.length === 0 && (
                        <CircularProgress />
                    )}
                    {transactions.length > 0 && (
                        <>{transactions.length} transactions found</>
                    )}
                    {fastpassInfo && haveFastpass && (
                        <div className={styles.fastpassInfo}>
                            <div className={styles.header}>Fastpass Info:</div>
                            <div>
                                Muni Rides Taken: {fastpassInfo.muniRidesTaken}
                            </div>
                            <div>
                                Bart Rides Taken: {fastpassInfo.bartRidesTaken}
                            </div>
                            <div>Transfers: {fastpassInfo.transfers}</div>
                            <div>
                                Cost Without Fastpass: $
                                {fastpassInfo.costWithoutFastpass.toFixed(2)}
                            </div>
                        </div>
                    )}
                    {isWorthIt && !haveFastpass && (
                        <div>
                            <div className={styles.header}>
                                Non-Fastpass Info:
                            </div>
                            <div>
                                Muni Rides Taken: {isWorthIt.muniRidesTaken}
                            </div>
                            <div>
                                Bart Rides Taken: {isWorthIt.bartRidesTaken}
                            </div>
                            <div>
                                Total Cost: ${isWorthIt.totalCost.toFixed(2)}
                            </div>
                            <div>
                                Muni-only Fastpass Worth It ($85):{" "}
                                {isWorthIt.muniOnlyFastpassWorthIt
                                    ? "Yes"
                                    : "No"}
                            </div>
                            <div>
                                Muni+BART Fastpass Worth It ($102):{" "}
                                {isWorthIt.muniBartFastpassWorthIt
                                    ? "Yes"
                                    : "No"}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
export default App;
