import "./ResultModal.css";
import type { AnalyzeResponse } from "../types/analyze-response";

type Props = {
  open: boolean;
  result: AnalyzeResponse | null;
  error: string | null;
  onClose: () => void;
  onRetry: () => void;
};

const ResultModal = ({ open, result, error, onClose, onRetry }: Props) => {
  if (!open) return null;

  const statusLabel = result?.is_phishing ? "PHISHING" : "SAFE";
  const riskLevel = result?.risk_level?.toUpperCase() ?? "UNKNOWN";

  return (
    <div className="result-overlay" role="dialog" aria-modal="true">
      <div className="result-card">
        <header>
          <h2>Scan Result</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close result modal">
            ×
          </button>
        </header>

        {error && (
          <div className="result-error">
            <p>{error}</p>
            <button onClick={onRetry}>Retry</button>
          </div>
        )}

        {!error && result && (
          <>
            <p className={`status ${result.is_phishing ? "phishing" : "safe"}`}>
              {statusLabel}
            </p>
            <p className={`risk-badge risk-${riskLevel.toLowerCase()}`}>
              Risk: {riskLevel}
            </p>
            <p className="reason">{result.reason ?? "No reason provided."}</p>

            {result.suspicious_elements && result.suspicious_elements.length > 0 && (
              <div className="details">
                <h3>Suspicious Elements</h3>
                <ul>
                  {result.suspicious_elements.map((elem, idx) => (
                    <li key={`${elem.type}-${idx}`}>
                      <strong>{elem.type}</strong>: {elem.value}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.recommended_action && (
              <p className="action">
                Recommended action:{" "}
                <strong>{result.recommended_action}</strong>
              </p>
            )}

            {result.extracted_urls && result.extracted_urls.length > 0 && (
              <div className="details">
                <h3>URLs Detected</h3>
                <ul>
                  {result.extracted_urls.map((url: string) => (
                    <li key={url}>
                      <a href={url} target="_blank" rel="noreferrer">
                        {url}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}

        {!error && (
          <div className="actions">
            <button onClick={onClose}>Close</button>
            <button onClick={onRetry}>Scan Again</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultModal;

