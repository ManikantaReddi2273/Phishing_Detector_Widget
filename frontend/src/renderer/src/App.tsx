import { useState } from "react";
import FloatingWidget from "./components/FloatingWidget";
import ResultModal from "./components/ResultModal";
import LoadingSpinner from "./components/LoadingSpinner";
import { scanScreen } from "./utils/api-client";
import type { AnalyzeResponse } from "./types/analyze-response";

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await scanScreen(true);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsProcessing(false);
    }
  };

  const closeResult = () => {
    setResult(null);
    setError(null);
  };

  const retry = () => {
    closeResult();
    void handleScan();
  };

  return (
    <div className="app-root">
      <FloatingWidget onClick={handleScan} loading={isProcessing} />
      {isProcessing && <LoadingSpinner />}
      <ResultModal
        open={!!result || !!error}
        onClose={closeResult}
        onRetry={retry}
        result={result}
        error={error}
      />
    </div>
  );
}

export default App;

