import "./LoadingSpinner.css";

const LoadingSpinner = () => {
  return (
    <div className="spinner-overlay" role="status" aria-live="polite">
      <div className="spinner" />
      <p>Analyzing text...</p>
    </div>
  );
};

export default LoadingSpinner;

