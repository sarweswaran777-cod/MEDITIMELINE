import sqlite3
import pandas as pd
from datetime import datetime
from auth import hash_password

DB_NAME = 'meditimeline.db'


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_database():
    conn = get_connection()
    c = conn.cursor()

    # ── users ──────────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        email TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1
    )''')

    # ── patients ───────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        medical_id TEXT PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        date_of_birth TEXT,
        age INTEGER,
        gender TEXT,
        blood_group TEXT,
        allergies TEXT,
        emergency_contact TEXT,
        phone TEXT,
        address TEXT,
        registered_by_hospital INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    # ── hospitals ──────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS hospitals (
        hospital_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        hospital_name TEXT,
        hospital_code TEXT,
        email TEXT,
        address TEXT,
        phone TEXT,
        authorized_doctor TEXT,
        status TEXT DEFAULT 'Pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    # ── medical_history ────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS medical_history (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medical_id TEXT,
        hospital_id INTEGER,
        hospital_name TEXT,
        doctor_name TEXT,
        event_date TEXT,
        event_type TEXT,
        description TEXT,
        diagnosis TEXT,
        medicine TEXT,
        test_result TEXT,
        surgery TEXT,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(medical_id) REFERENCES patients(medical_id),
        FOREIGN KEY(hospital_id) REFERENCES hospitals(hospital_id)
    )''')

    # ── consent_requests ───────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS consent_requests (
        consent_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medical_id TEXT,
        hospital_id INTEGER,
        reason TEXT,
        status TEXT DEFAULT 'Pending',
        requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        approved_at DATETIME,
        expiry_date DATETIME,
        FOREIGN KEY(medical_id) REFERENCES patients(medical_id),
        FOREIGN KEY(hospital_id) REFERENCES hospitals(hospital_id)
    )''')

    # ── audit_logs ─────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        action TEXT,
        medical_id TEXT,
        hospital_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    # ── documents ──────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        document_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medical_id TEXT,
        hospital_id INTEGER,
        document_type TEXT,
        file_name TEXT,
        file_path TEXT,
        ocr_text TEXT,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(medical_id) REFERENCES patients(medical_id),
        FOREIGN KEY(hospital_id) REFERENCES hospitals(hospital_id)
    )''')

    conn.commit()

    # ── Safe migrations for existing databases ─────────────────────────
    _safe_migrate(conn)

    conn.close()


def _safe_migrate(conn):
    """Add missing columns to existing tables without destroying data."""
    c = conn.cursor()

    # hospitals – add missing columns
    _add_column_if_missing(c, 'hospitals', 'hospital_code', 'TEXT')
    _add_column_if_missing(c, 'hospitals', 'email', 'TEXT')
    _add_column_if_missing(c, 'hospitals', 'phone', 'TEXT')
    _add_column_if_missing(c, 'hospitals', 'status', "TEXT DEFAULT 'Approved'")

    # patients – add missing columns
    _add_column_if_missing(c, 'patients', 'phone', 'TEXT')
    _add_column_if_missing(c, 'patients', 'address', 'TEXT')
    _add_column_if_missing(c, 'patients', 'registered_by_hospital', 'INTEGER')

    # medical_history – add missing columns
    _add_column_if_missing(c, 'medical_history', 'hospital_name', 'TEXT')
    _add_column_if_missing(c, 'medical_history', 'surgery', 'TEXT')
    _add_column_if_missing(c, 'medical_history', 'notes', 'TEXT')

    # audit_logs – add missing columns
    _add_column_if_missing(c, 'audit_logs', 'hospital_id', 'TEXT')

    # documents – add missing columns
    _add_column_if_missing(c, 'documents', 'ocr_text', 'TEXT')

    # Migrate old integer 'approved' column → text 'status' if needed
    # If old column 'approved' exists, migrate values
    c.execute("PRAGMA table_info(hospitals)")
    cols = [row[1] for row in c.fetchall()]
    if 'approved' in cols:
        c.execute("UPDATE hospitals SET status='Approved' WHERE approved=1 AND (status IS NULL OR status='')")
        c.execute("UPDATE hospitals SET status='Pending' WHERE approved=0 AND (status IS NULL OR status='')")

    conn.commit()


def _add_column_if_missing(cursor, table, column, col_type):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


# ════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ════════════════════════════════════════════════════════════════════════

def create_user(username, password, role, email=""):
    conn = get_connection()
    c = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)",
            (username, pwd_hash, role, email)
        )
        conn.commit()
        user_id = c.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def authenticate_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, password_hash, role, active FROM users WHERE username=?",
        (username,)
    )
    user = c.fetchone()
    conn.close()
    return user


def toggle_user_active(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET active = CASE WHEN active=1 THEN 0 ELSE 1 END WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════
# HOSPITAL MANAGEMENT
# ════════════════════════════════════════════════════════════════════════

def register_hospital(user_id, hospital_name, hospital_code, email, phone, address, authorized_doctor):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO hospitals
           (user_id, hospital_name, hospital_code, email, phone, address, authorized_doctor, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')""",
        (user_id, hospital_name, hospital_code, email, phone, address, authorized_doctor)
    )
    conn.commit()
    hid = c.lastrowid
    conn.close()
    return hid


def get_hospital_by_userid(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM hospitals WHERE user_id=?", (user_id,))
    columns = [col[0] for col in c.description] if c.description else []
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(columns, row))
    return None


def get_hospital_by_id(hospital_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM hospitals WHERE hospital_id=?", (hospital_id,))
    columns = [col[0] for col in c.description] if c.description else []
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(columns, row))
    return None


def get_all_hospitals():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT h.*, u.username, u.email as user_email, u.active as user_active
           FROM hospitals h LEFT JOIN users u ON h.user_id = u.id
           ORDER BY h.created_at DESC""",
        conn
    )
    conn.close()
    return df


def get_pending_hospitals():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT h.*, u.username FROM hospitals h
           LEFT JOIN users u ON h.user_id = u.id
           WHERE h.status='Pending' ORDER BY h.created_at DESC""",
        conn
    )
    conn.close()
    return df


def approve_hospital(hospital_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE hospitals SET status='Approved' WHERE hospital_id=?", (hospital_id,))
    conn.commit()
    conn.close()


def reject_hospital(hospital_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE hospitals SET status='Rejected' WHERE hospital_id=?", (hospital_id,))
    conn.commit()
    conn.close()


def get_hospital_approval_status(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status FROM hospitals WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None


def update_hospital(hospital_id, hospital_name=None, email=None, phone=None, address=None, authorized_doctor=None):
    conn = get_connection()
    c = conn.cursor()
    if hospital_name is not None:
        c.execute("UPDATE hospitals SET hospital_name=? WHERE hospital_id=?", (hospital_name, hospital_id))
    if email is not None:
        c.execute("UPDATE hospitals SET email=? WHERE hospital_id=?", (email, hospital_id))
    if phone is not None:
        c.execute("UPDATE hospitals SET phone=? WHERE hospital_id=?", (phone, hospital_id))
    if address is not None:
        c.execute("UPDATE hospitals SET address=? WHERE hospital_id=?", (address, hospital_id))
    if authorized_doctor is not None:
        c.execute("UPDATE hospitals SET authorized_doctor=? WHERE hospital_id=?", (authorized_doctor, hospital_id))
    conn.commit()
    conn.close()


def toggle_hospital_status(hospital_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM hospitals WHERE hospital_id=?", (hospital_id,))
    row = c.fetchone()
    if row:
        toggle_user_active(row[0])
    conn.close()


def get_hospital_stats(hospital_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT medical_id) FROM medical_history WHERE hospital_id=?", (hospital_id,))
    patients = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM medical_history WHERE hospital_id=?", (hospital_id,))
    records = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM consent_requests WHERE hospital_id=? AND status='Pending'", (hospital_id,))
    pending = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM consent_requests WHERE hospital_id=? AND status='Approved'", (hospital_id,))
    approved = c.fetchone()[0]
    conn.close()
    return {
        "patients": patients,
        "records": records,
        "pending_requests": pending,
        "approved_access": approved
    }


# ════════════════════════════════════════════════════════════════════════
# PATIENT MANAGEMENT
# ════════════════════════════════════════════════════════════════════════

def generate_medical_id():
    """Generate sequential Medical ID like MED2026001."""
    conn = get_connection()
    c = conn.cursor()
    year = datetime.now().year
    c.execute(
        "SELECT medical_id FROM patients WHERE medical_id LIKE ? ORDER BY medical_id DESC LIMIT 1",
        (f"MED{year}%",)
    )
    row = c.fetchone()
    conn.close()
    if row:
        try:
            last_num = int(row[0][7:])  # MED2026XXX → digits after year
            return f"MED{year}{last_num + 1:03d}"
        except Exception:
            pass
    return f"MED{year}001"


def add_patient(medical_id, user_id, name, dob, age, gender, blood, allergies, emergency,
                phone="", address="", registered_by_hospital=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO patients
           (medical_id, user_id, name, date_of_birth, age, gender, blood_group,
            allergies, emergency_contact, phone, address, registered_by_hospital)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (medical_id, user_id, name, dob, age, gender, blood, allergies, emergency,
         phone, address, registered_by_hospital)
    )
    conn.commit()
    conn.close()


def get_patient(medical_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE medical_id=?", (medical_id,))
    columns = [col[0] for col in c.description] if c.description else []
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(columns, row))
    return None


def get_patient_by_userid(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE user_id=?", (user_id,))
    columns = [col[0] for col in c.description] if c.description else []
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(columns, row))
    return None


def get_all_patients():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients ORDER BY created_at DESC", conn)
    conn.close()
    return df


# ════════════════════════════════════════════════════════════════════════
# MEDICAL RECORDS
# ════════════════════════════════════════════════════════════════════════

def add_medical_record(medical_id, hospital_id, hospital_name, doctor, event_date,
                       event_type, desc, diagnosis, medicine, test_result,
                       surgery="", notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO medical_history
           (medical_id, hospital_id, hospital_name, doctor_name, event_date, event_type,
            description, diagnosis, medicine, test_result, surgery, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (medical_id, hospital_id, hospital_name, doctor, event_date, event_type,
         desc, diagnosis, medicine, test_result, surgery, notes)
    )
    conn.commit()
    conn.close()


def get_history(medical_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM medical_history WHERE medical_id=? ORDER BY event_date DESC",
        conn, params=(medical_id,)
    )
    conn.close()
    return df


def get_all_records():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT mh.*, p.name as patient_name
           FROM medical_history mh
           LEFT JOIN patients p ON mh.medical_id = p.medical_id
           ORDER BY mh.created_at DESC""",
        conn
    )
    conn.close()
    return df


# ════════════════════════════════════════════════════════════════════════
# CONSENT / ACCESS
# ════════════════════════════════════════════════════════════════════════

def request_consent(medical_id, hospital_id, reason):
    conn = get_connection()
    c = conn.cursor()
    # Check if already a pending/approved request
    c.execute(
        "SELECT consent_id FROM consent_requests WHERE medical_id=? AND hospital_id=? AND status IN ('Pending','Approved')",
        (medical_id, hospital_id)
    )
    existing = c.fetchone()
    if existing:
        conn.close()
        return False
    c.execute(
        "INSERT INTO consent_requests (medical_id, hospital_id, reason, status) VALUES (?, ?, ?, 'Pending')",
        (medical_id, hospital_id, reason)
    )
    conn.commit()
    conn.close()
    return True


def approve_consent(consent_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE consent_requests SET status='Approved', approved_at=CURRENT_TIMESTAMP WHERE consent_id=?",
        (consent_id,)
    )
    conn.commit()
    conn.close()


def reject_consent(consent_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE consent_requests SET status='Rejected' WHERE consent_id=?", (consent_id,))
    conn.commit()
    conn.close()


def revoke_consent(medical_id, hospital_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE consent_requests SET status='Revoked' WHERE medical_id=? AND hospital_id=?",
        (medical_id, hospital_id)
    )
    conn.commit()
    conn.close()


def check_hospital_access(medical_id, hospital_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT status FROM consent_requests WHERE medical_id=? AND hospital_id=? AND status='Approved'",
        (medical_id, hospital_id)
    )
    row = c.fetchone()
    conn.close()
    return row is not None


def get_pending_requests(medical_id):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT c.*, h.hospital_name FROM consent_requests c
           JOIN hospitals h ON c.hospital_id = h.hospital_id
           WHERE c.medical_id=? AND c.status='Pending'""",
        conn, params=(medical_id,)
    )
    conn.close()
    return df


def get_patient_consents(medical_id):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT c.*, h.hospital_name FROM consent_requests c
           JOIN hospitals h ON c.hospital_id = h.hospital_id
           WHERE c.medical_id=? AND c.status='Approved'""",
        conn, params=(medical_id,)
    )
    conn.close()
    return df


def get_hospital_pending_consents(hospital_id):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT c.*, p.name as patient_name FROM consent_requests c
           JOIN patients p ON c.medical_id = p.medical_id
           WHERE c.hospital_id=? AND c.status='Pending'""",
        conn, params=(hospital_id,)
    )
    conn.close()
    return df


def get_hospital_approved_consents(hospital_id):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT c.*, p.name as patient_name FROM consent_requests c
           JOIN patients p ON c.medical_id = p.medical_id
           WHERE c.hospital_id=? AND c.status='Approved'""",
        conn, params=(hospital_id,)
    )
    conn.close()
    return df


# ════════════════════════════════════════════════════════════════════════
# AUDIT LOGS
# ════════════════════════════════════════════════════════════════════════

def add_audit_log(user_id, role, action, medical_id="", hospital_id=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_logs (user_id, role, action, medical_id, hospital_id) VALUES (?, ?, ?, ?, ?)",
        (user_id, role, action, medical_id, str(hospital_id))
    )
    conn.commit()
    conn.close()


def get_audit_logs(limit=100):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT al.*, u.username FROM audit_logs al
           LEFT JOIN users u ON al.user_id = u.id
           ORDER BY al.timestamp DESC LIMIT ?""",
        conn, params=(limit,)
    )
    conn.close()
    return df


# ════════════════════════════════════════════════════════════════════════
# DOCUMENTS
# ════════════════════════════════════════════════════════════════════════

def save_document(medical_id, hospital_id, doc_type, filename, filepath, ocr_text=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO documents
           (medical_id, hospital_id, document_type, file_name, file_path, ocr_text)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (medical_id, hospital_id, doc_type, filename, filepath, ocr_text)
    )
    conn.commit()
    conn.close()


def get_documents(medical_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM documents WHERE medical_id=? ORDER BY uploaded_at DESC",
        conn, params=(medical_id,)
    )
    conn.close()
    return df


def get_all_documents():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT d.*, p.name as patient_name FROM documents d
           LEFT JOIN patients p ON d.medical_id = p.medical_id
           ORDER BY d.uploaded_at DESC""",
        conn
    )
    conn.close()
    return df


# ════════════════════════════════════════════════════════════════════════
# DASHBOARD STATISTICS
# ════════════════════════════════════════════════════════════════════════

def get_dashboard_statistics():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM patients")
    patients = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM hospitals")
    hospitals = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM hospitals WHERE status='Pending'")
    pending_hospitals = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM hospitals WHERE status='Approved'")
    approved_hospitals = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM medical_history")
    records = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM audit_logs")
    logs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM documents")
    docs = c.fetchone()[0]
    conn.close()
    return {
        "patients": patients,
        "hospitals": hospitals,
        "pending_hospitals": pending_hospitals,
        "approved_hospitals": approved_hospitals,
        "records": records,
        "logs": logs,
        "documents": docs
    }


# ════════════════════════════════════════════════════════════════════════
# DEMO DATA
# ════════════════════════════════════════════════════════════════════════

def add_demo_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Create demo users
        admin_id = create_user("admin", "Admin@123", "Admin", "admin@meditimeline.com")
        hosp_uid = create_user("cityhospital", "Hospital@123", "Hospital", "cityhospital@example.com")
        pat_id = create_user("rahul", "Patient@123", "Patient", "rahul@example.com")

        # Register demo hospital (pre-approved for demo)
        conn2 = get_connection()
        c2 = conn2.cursor()
        c2.execute(
            """INSERT INTO hospitals
               (user_id, hospital_name, hospital_code, email, phone, address, authorized_doctor, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'Approved')""",
            (hosp_uid, "City Hospital", "CITYHOSP001",
             "cityhospital@example.com", "+91 9000000001",
             "MG Road, Bengaluru, Karnataka", "Dr. Rajesh Smith")
        )
        h_id = c2.lastrowid
        conn2.commit()

        # Register demo patient
        c2.execute(
            """INSERT INTO patients
               (medical_id, user_id, name, date_of_birth, age, gender,
                blood_group, allergies, emergency_contact, phone, address, registered_by_hospital)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("MED2026001", pat_id, "Rahul Kumar", "2002-05-15", 24, "Male",
             "O+", "Penicillin", "+91 9876543210", "+91 9876543210",
             "12, Anna Nagar, Chennai, Tamil Nadu", h_id)
        )

        # Grant demo hospital access to demo patient
        c2.execute(
            "INSERT INTO consent_requests (medical_id, hospital_id, reason, status, approved_at) VALUES (?, ?, ?, 'Approved', CURRENT_TIMESTAMP)",
            ("MED2026001", h_id, "Primary care hospital – pre-authorized")
        )

        # Demo medical history
        history = [
            ("MED2026001", h_id, "City Hospital", "Dr. A Sharma", "2002-05-15", "Birth Record",
             "Born healthy", "Healthy birth, no complications", "", "", "", ""),
            ("MED2026001", h_id, "City Hospital", "Dr. B Nair", "2005-06-15", "Vaccination",
             "Polio Drop – National Immunization", "", "Polio", "", "", ""),
            ("MED2026001", h_id, "City Hospital", "Dr. C Pillai", "2010-08-20", "Hospital Visit",
             "Severe Fever with chills, 3-day admission", "Viral Fever", "Paracetamol, Cetirizine", "", "", ""),
            ("MED2026001", h_id, "City Hospital", "Dr. D Menon", "2018-03-10", "Surgery",
             "Emergency Appendix Removal", "Appendicitis", "Antibiotics, Painkillers", "Success", "Appendectomy", "Full recovery in 2 weeks"),
            ("MED2026001", h_id, "City Hospital", "Dr. E Kumar", "2022-11-05", "Diagnosis",
             "High Blood Sugar detected", "Type 2 Diabetes Mellitus", "Metformin 500mg", "Fasting Glucose: 150 mg/dl", "", "Monthly monitoring advised"),
            ("MED2026001", h_id, "City Hospital", "Dr. F Iyer", "2025-02-14", "Cancer Checkup",
             "Routine Cancer Screening", "Clear – No abnormality", "", "All reports negative", "", "Annual checkup recommended"),
            ("MED2026001", h_id, "City Hospital", "Dr. G Rao", "2026-08-10", "Follow-up",
             "Diabetes Follow-up visit", "Stable – Type 2 Diabetes", "Metformin 500mg", "Glucose: 118 mg/dl", "", "Condition improving"),
        ]
        for h in history:
            c2.execute(
                """INSERT INTO medical_history
                   (medical_id, hospital_id, hospital_name, doctor_name, event_date, event_type,
                    description, diagnosis, medicine, test_result, surgery, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                h
            )

        # Audit log entries for demo
        c2.execute(
            "INSERT INTO audit_logs (user_id, role, action, medical_id) VALUES (?, 'Admin', 'System initialized with demo data', '')",
            (admin_id,)
        )
        conn2.commit()
        conn2.close()

    conn.close()
