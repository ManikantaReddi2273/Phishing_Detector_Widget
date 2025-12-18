# OS-Level AI Phishing Detection System  
## Phased Implementation Plan

---

## Phase 1: Foundation & OS-Level Setup
**Goal:** Create a stable OS-level application skeleton.

- Set up Python project structure  
- Create always-on-top floating widget (Protection ON/OFF)  
- Detect active window and application metadata  
- Implement background service loop  

---

## Phase 2: Screen Capture & Accessibility Integration
**Goal:** Acquire text from any running application.

- Capture active window screenshots using MSS  
- Integrate Windows UI Automation for accessibility text  
- Handle window switches and content refresh  

---

## Phase 3: OCR & Text Extraction
**Goal:** Convert visual data into usable text.

- Integrate EasyOCR for screen text extraction  
- Merge OCR text with accessibility text  
- Noise removal and duplicate filtering  

---

## Phase 4: Text Processing & Chunking
**Goal:** Prepare text for LLM analysis.

- Clean UI artifacts and irrelevant tokens  
- Implement logical chunking (300–700 words)  
- Maintain rolling context for long documents  

---

## Phase 5: Groq LLM Integration
**Goal:** Perform intelligent phishing detection.

- Integrate Groq API with secure key handling  
- Design phishing-detection prompts  
- Parse structured JSON responses  

---

## Phase 6: Decision Engine & Risk Scoring
**Goal:** Aggregate results and determine final alerts.

- Combine results from multiple text chunks  
- Implement risk-level logic (Low / Medium / High)  
- Trigger alerts based on thresholds  

---

## Phase 7: UI Alerts & User Interaction
**Goal:** Notify users clearly and safely.

- Update widget color/status dynamically  
- Show explanation and suspicious text  
- Allow user to pause or disable detection  

---

## Phase 8: Optimization, Security & Testing
**Goal:** Make the system robust and ethical.

- Optimize OCR frequency and API calls  
- Ensure no data is stored permanently  
- Test across browsers, Notepad, PDFs, emails  

---

## Phase 9: Documentation & Presentation
**Goal:** Prepare for academic and interview evaluation.

- Prepare final project report  
- Create architecture diagrams  
- Prepare demo and explanation flow  
