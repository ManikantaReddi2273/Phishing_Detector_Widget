import "./FloatingWidget.css";

type Props = {
  onClick: () => void;
  loading: boolean;
};

const FloatingWidget = ({ onClick, loading }: Props) => {
  return (
    <button
      className="floating-widget"
      onClick={onClick}
      disabled={loading}
      title="Scan screen for phishing"
      aria-busy={loading}
    >
      {loading ? "Scanning..." : "Scan"}
    </button>
  );
};

export default FloatingWidget;

