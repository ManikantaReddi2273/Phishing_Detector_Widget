# Phishing Guard

Phishing Guard is a real-time phishing detection system that monitors active windows and visual content changes to identify potential phishing attempts. It combines system-level monitoring, image processing, text extraction, and AI-based analysis to ensure accurate and efficient detection.

## Features

- **Real-Time Detection**: Monitors active windows and visual changes to detect phishing attempts.
- **Floating Widget**: Displays risk levels and allows user interaction (pause/resume, view details).
- **Visual Change Detection**: Detects scrolling, dynamic content updates, and page changes.
- **Text Extraction**: Uses OCR and accessibility APIs to extract text from applications.
- **AI Analysis**: Leverages GPT-based models to analyze text for phishing risks.

## Tech Stack

- **Python**: Core programming language.
- **PyQt5**: GUI framework for the floating widget.
- **OpenCV**: Image processing for screenshot capture and visual change detection.
- **NumPy**: Numerical computation for image comparison.
- **Tesseract OCR**: Optical Character Recognition for text extraction.
- **GPT (LLM Integration)**: AI-based phishing analysis.
- **Windows APIs**: System-level monitoring of active windows.
- **Threading**: Background processing for smooth operation.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/phishing_guard.git
   cd phishing_guard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

- **Pause Detection**: Click the "Pause" button on the floating widget.
- **View Details**: Click the "ⓘ" button to see risk levels and reasons.
- **Drag Widget**: Move the widget by dragging it.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or support, contact [your-email@example.com](mailto:your-email@example.com).