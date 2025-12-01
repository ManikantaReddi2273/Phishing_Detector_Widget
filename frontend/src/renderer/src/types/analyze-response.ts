export type SuspiciousElement = {
  type: string;
  value: string;
  confidence: number;
};

export type AnalyzeResponse = {
  is_phishing: boolean;
  risk_level: string;
  reason: string;
  recommended_action?: string;
  suspicious_elements?: SuspiciousElement[];
  extracted_urls?: string[];
};

