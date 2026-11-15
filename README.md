# 🛡️ PrivacyGuard AI – Automated Personal Data Protection and Sensitive Information Detection System

An AI-powered, privacy-first cybersecurity application designed to detect Personally Identifiable Information (PII), assess privacy risks and automatically sanitize sensitive data from documents and text inputs.

PrivacyGuard AI combines Natural Language Processing (NLP), Named Entity Recognition (NER) and Regular Expressions (Regex) to identify sensitive information, calculate privacy risk scores and generate sanitized documents through an interactive Streamlit dashboard.

---

## 📌 Overview

PrivacyGuard AI is designed to help protect sensitive personal and confidential information by automatically detecting and masking PII in uploaded documents and manually entered text.

The system analyses documents, identifies sensitive information and evaluates potential privacy risks using a scoring mechanism.

### Users can:

- Upload PDF, DOCX and TXT documents.
- Enter text manually for privacy analysis.
- Detect personal information such as names, emails and phone numbers.
- Identify government IDs such as Aadhaar and PAN.
- Detect financial information and API credentials.
- Calculate a privacy risk score between 0 and 100.
- Automatically redact sensitive information.
- Choose between full redaction and partial masking.
- Download sanitized documents in multiple formats.
- View privacy analysis and scanning statistics.

The application uses a hybrid detection approach combining spaCy NLP and Regex-based pattern matching. Sensitive document processing is designed around in-memory handling using Python memory buffers.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔒 In-Memory Document Processing | Uses io.BytesIO memory buffers for document processing without writing original document contents to temporary disk files. |
| 🧠 Hybrid AI Detection Engine | Combines spaCy Named Entity Recognition and Regex-based detection. |
| 🪪 PII Detection | Identifies names, email addresses, phone numbers, addresses and dates of birth. |
| 🏛️ Government ID Detection | Detects Indian Aadhaar and PAN number patterns. |
| 💳 Financial Data Detection | Identifies credit and debit card number patterns. |
| 🔑 Secret Detection | Detects supported API keys, tokens and password patterns. |
| 📊 Privacy Risk Score | Calculates a privacy risk score from 0–100 using sensitivity weights and correlation rules. |
| 🎭 Full Redaction | Completely replaces detected sensitive information with labels such as [REDACTED: EMAIL]. |
| 🛡️ Partial Masking | Hides sensitive characters while preserving readability (e.g. u****@example.com). |
| 📄 Multi-Format Document Support | Supports PDF, DOCX and TXT document ingestion and sanitized output generation. |
| 🎨 Cybersecurity Dashboard | Provides a modern dark-themed interface with privacy monitoring components. |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Programming Language | Python 3.9+ |
| Frontend / UI | Streamlit |
| NLP Framework | spaCy |
| Named Entity Recognition | en_core_web_sm |
| Pattern Detection | Python Regular Expressions (re) |
| Data Processing | Pandas |
| PDF Processing | PyPDF |
| Word Document Processing | python-docx |
| PDF Generation | ReportLab |
| Memory Processing | io.BytesIO |
| Cryptographic Hashing | hashlib (SHA-256) |
| Styling | Custom CSS3 and HTML5 |
| Development Environment | VS Code / Antigravity IDE |

**Important:** PrivacyGuard AI uses spaCy NLP and deterministic Regex detection. It does not require external LLM APIs for its detection pipeline, supporting local execution without external AI API latency.

---

## 🗂️ Project Structure

```text
PrivacyGuardAI/
│
├── .streamlit/
│   └── config.toml
│
├── sample_documents/
│   ├── sample_resume.txt
│   ├── employee_kyc_record.txt
│   └── medical_intake_form.txt
│
├── app.py
├── components.py
├── data_handler.py
├── detector.py
├── risk_assessment.py
├── masking.py
├── masking_engine.py
├── document_generator.py
├── styles.py
├── telemetry.py
├── views.py
│
├── test_complete_application.py
├── test_detector.py
├── test_risk.py
├── test_masking_and_download.py
├── test_modules.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## ⚙️ How It Works

PrivacyGuard AI follows an automated five-stage privacy protection workflow:

```text
       Document / Text Input
                |
                v
        1. Data Ingestion
        (PDF, DOCX, TXT, Form)
                |
                v
         2. PII Detection
         (Regex + spaCy NER)
                |
                v
    3. Privacy Risk Assessment
         (0–100 Risk Scoring)
                |
                v
        4. Data Sanitization
        (Full / Partial Masking)
                |
                v
        5. Secure Document Export
           (PDF / DOCX / TXT)
                |
                v
          Sanitized Output
```

### Five-Stage Workflow Details

#### Stage 1 – Data Ingestion

- Accepts uploaded PDF, DOCX and TXT files.
- Supports manually entered text.
- Reads document contents using in-memory processing.
- Validates supported file formats.

#### Stage 2 – PII Detection

- Uses spaCy NLP to identify contextual entities.
- Uses Regex patterns to identify structured information.
- Detects sensitive information such as names, emails, phone numbers, Aadhaar, PAN and API keys.
- Records the detected text positions for accurate masking.

#### Stage 3 – Privacy Risk Assessment

- Assigns sensitivity weights to detected information.
- Calculates an overall privacy risk score between 0 and 100.
- Applies compound correlation multipliers for combinations of sensitive information.
- Categorizes the risk as Low, Medium or Critical.

#### Stage 4 – Data Sanitization

Provides two masking options:

- **Full Redaction:** Completely replaces sensitive information (e.g., `[REDACTED: EMAIL]`).
- **Partial Masking:** Hides selected characters while preserving readability (e.g., `u****@example.com`).
- Uses **reverse-index masking** to preserve original text positions during multiple replacements.

#### Stage 5 – Secure Export

- Generates sanitized TXT files.
- Generates sanitized DOCX files.
- Generates sanitized PDF reports via ReportLab.
- Generates SHA-256 fingerprints for document deduplication.

---

## 🔍 PII Detection Categories

| Category | Examples |
|---|---|
| **Personal Information** | Names, email addresses, phone numbers and dates of birth. |
| **Residential Information** | Address patterns and location-related information. |
| **Government Identifiers** | Aadhaar (12-digit pattern) and PAN (10-character alphanumeric pattern). |
| **Financial Information** | Credit and debit card number patterns. |
| **Digital Credentials** | API keys (GitHub, Google, Stripe), tokens and password patterns. |

---

## 📊 Privacy Risk Assessment

PrivacyGuard AI calculates a privacy risk score between 0 and 100.

The scoring mechanism considers:

- Type of detected sensitive information.
- Sensitivity weights assigned to each category.
- Number of detected entities.
- Combinations of sensitive information.
- Compound correlation multipliers.

### Risk Categories

| Risk Score | Risk Level |
|---|---|
| **0–30** | 🟢 LOW |
| **31–60** | 🟡 MEDIUM |
| **61–100** | 🔴 CRITICAL / HIGH |

---

## 🎭 Data Masking Methods

PrivacyGuard AI supports two sanitization modes:

### 1. Full Redaction

Completely replaces detected sensitive information.

- **Original:** `Email: user@example.com`
- **Sanitized:** `Email: [REDACTED: EMAIL]`

### 2. Partial Masking

Preserves limited information while hiding sensitive characters.

- **Original:** `user@example.com`
- **Sanitized:** `u****@example.com`

---

## 📄 Document Processing and Export

- **Supported Input Formats:** PDF (`.pdf`), Microsoft Word (`.docx`), Plain Text (`.txt`), and manual text form entry.
- **Supported Output Formats:** Sanitized PDF (`.pdf`), Sanitized Word (`.docx`), and Sanitized Text (`.txt`).

---

## 💻 How to Use

1. **Open PrivacyGuard AI:** Launch the application and explore the privacy protection dashboard.
2. **Upload a Document:** Upload a PDF, DOCX or TXT file, or enter text manually.
3. **Detect Sensitive Information:** The detection engine scans the content using Regex and spaCy NLP.
4. **Review Privacy Risk:** View the detected entities and the calculated privacy risk score.
5. **Select Masking Method:** Choose Full Redaction or Partial Masking.
6. **Generate Sanitized Output:** The application replaces detected sensitive information according to the selected masking method.
7. **Download the Result:** Download the sanitized document in PDF, DOCX or TXT format.

---

## 🔮 Future Enhancements

- Improved contextual PII detection.
- Support for additional international identity formats.
- Multilingual PII detection.
- Advanced document structure preservation.
- Customizable masking policies.
- Improved detection accuracy and false-positive reduction.
- Role-based access control.
- Enhanced security audit logs.
- Additional document formats.
- Enterprise deployment and integration.

---

## 👩‍💻 Developed By

**Author:** Bhanushree G  
**Department:** Computer Science and Engineering – Data Science  
**Institution:** Nagarjuna College of Engineering and Technology (NCET)

---
