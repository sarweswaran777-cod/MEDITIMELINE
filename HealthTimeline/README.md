# MEDI TIMELINE

**MEDI TIMELINE** is an AI-Powered Medical History Intelligence and Secure Patient Record Management System featuring longitudinal electronic health records (EHR), granular consent management, and clinical decision support.

---

## Clinical & Safety Notice
*The MEDI TIMELINE clinical decision-support module synthesizes structured longitudinal patient health records to assist attending healthcare providers. All automated clinical findings, medication logs, and diagnostic summaries are designed for clinical reference and must be verified by licensed medical professionals during patient evaluation.*

---

## Core System Architecture & Features

### 1. Multi-Tier Role-Based Access Control (RBAC)
- **System Administrator Console**: Facility verification workflow, hospital directory management, master patient index oversight, and immutable security audit logs.
- **Healthcare Facility Workspace**: Patient onboarding with automated Medical ID generation, chart search with consent enforcement, clinical encounter entry, period-based clinical intelligence summary, and optical document scanner.
- **Patient Health Portal**: Self-governed personal medical timeline (read-only clinical records to ensure audit integrity), dynamic Emergency Medical Alert card, and granular hospital consent governance (approve, deny, revoke).

### 2. Longitudinal Medical History Intelligence
- **Period-Based Clinical Synthesis**: Filter health history across customizable intervals (All Time, 30 Days, 3 Months, 6 Months, 1 Year, or Custom Date Range).
- **Separation of Source Records vs. Clinical Insights**: Directly contrasts verified EHR records (diagnoses, pharmacotherapy, procedures, lab panels) against rule-based clinical decision support insights (glycemic surveillance, surgical follow-up tracking, antimicrobial reconciliation).
- **Zero Hallucination Guarantee**: Intelligence summaries strictly reflect stored clinical records without fabricating medical diagnoses or medications.

### 3. Patient-Centric Consent & Security Architecture
- **Consent Governance**: Healthcare facilities cannot inspect patient records without approved, patient-granted consent.
- **Cryptographic Security**: Passwords hashed using industry-standard `bcrypt` with unique salts.
- **Immutable Audit Logging**: Every authentication event, consent request, record creation, and chart access is tracked with user ID, role, action, and timestamps.
- **SQL Injection Prevention**: Parameterized queries across all database operations.

---

## Technology Stack
- **Application Framework**: Python 3.8+ / Streamlit
- **Data Architecture**: SQLite with parameterized transactions & pandas
- **Authentication & Cryptography**: bcrypt
- **UI Design System**: Clean healthcare design system with deep navy, clinical teal, and white aesthetic

---

## Folder Structure
```
HealthTimeline/
├── app.py              # Main Streamlit web application & dashboards
├── database.py         # SQLite schema, queries, migrations & audit trail
├── auth.py             # Bcrypt password hashing & session authentication
├── ai_summary.py       # Clinical intelligence synthesis & date range filtering
├── ocr.py              # Medical document optical scanner & field extraction
├── requirements.txt    # Application dependencies
├── README.md           # System documentation & deployment guide
├── uploads/            # Secure document attachment repository
└── meditimeline.db     # SQLite electronic health records database
```

---

## Installation & Setup

1. **Verify Python Installation** (Python 3.8 or higher):
   ```bash
   python --version
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application
Launch the web dashboard with Streamlit:
```bash
streamlit run app.py
```

---

## System Evaluation Credentials

| Portal / Role | Username | Password | Key Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@123` | Hospital verification, user account management, audit logs |
| **Healthcare Facility** | `cityhospital` | `Hospital@123` | Patient enrollment, medical encounter filing, AI clinical summary |
| **Patient Portal** | `rahul` | `Patient@123` | View personal timeline, emergency card, hospital consent management |

---

## Regulatory & Operational Scope
- **Data Storage**: Local SQLite database with automated schema migration.
- **Interoperability**: Standardized structured health record format ready for integration with national health stack frameworks (e.g. ABDM / FHIR).
- **Document Management**: Locally preserved clinical attachments with assisted clinician verification.
