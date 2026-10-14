"""
MEDI TIMELINE – AI-Powered Medical History Intelligence & Secure Patient Record System
Role-Based Electronic Health Record (EHR) & Clinical Decision-Support Management System
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

import database as db
import auth
import ai_summary
import ocr as ocr_module

# ── Page Configuration ──────────────────────────────────────────────────
st.set_page_config(
    page_title="MediTimeline — Clinical Health Record System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global Healthcare UI Design System (CSS) ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
}

/* Background & Main Layout */
.stApp {
    background-color: #f8fafc;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b192c 0%, #0f2942 100%) !important;
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #f8fafc !important;
    width: 100%;
    border-radius: 8px;
    padding: 8px 12px;
    font-weight: 500;
    font-size: 0.9rem;
    margin: 3px 0;
    text-align: left;
    transition: all 0.2s ease-in-out;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(13, 148, 136, 0.35);
    border-color: #0d9488;
    color: #ffffff !important;
    transform: translateX(3px);
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-top: 3px solid #0d9488;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
[data-testid="stMetricValue"] {
    color: #0f2942 !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
}
[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Form Controls & Buttons */
.stButton > button[kind="primary"] {
    background: #0d9488 !important;
    border-color: #0d9488 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    box-shadow: 0 2px 6px rgba(13, 148, 136, 0.25) !important;
    transition: all 0.2s ease;
}
.stButton > button[kind="primary"]:hover {
    background: #0f766e !important;
    border-color: #0f766e !important;
    box-shadow: 0 4px 10px rgba(13, 148, 136, 0.35) !important;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 500;
}

/* Tab Headers */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid #e2e8f0;
}
.stTabs [data-baseweb="tab"] {
    height: 44px;
    border-radius: 8px 8px 0 0;
    padding: 8px 18px;
    font-weight: 600;
    color: #64748b;
}
.stTabs [aria-selected="true"] {
    color: #0f2942 !important;
    border-bottom: 3px solid #0d9488 !important;
}

/* Headings */
h1 { color: #0f2942; font-weight: 700; font-size: 1.85rem; }
h2 { color: #0f2942; font-weight: 600; font-size: 1.45rem; }
h3 { color: #1e3a5f; font-weight: 600; font-size: 1.2rem; }
h4 { color: #1e3a5f; font-weight: 600; font-size: 1rem; }

/* Custom Clinical Dashboard Cards */
.med-header-card {
    background: linear-gradient(135deg, #0f2942 0%, #163e63 100%);
    color: white;
    padding: 22px 26px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(15, 41, 66, 0.08);
}
.med-header-card h2, .med-header-card h1 {
    color: #ffffff !important;
    margin: 0;
}
.med-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}

/* Status Badges */
.badge-approved {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
}
.badge-pending {
    background: #fffbeb;
    color: #92400e;
    border: 1px solid #fde68a;
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
}
.badge-rejected {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
}

/* Medical Timeline Card */
.timeline-record {
    border-left: 4px solid #0d9488;
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 0 10px 10px 0;
    padding: 16px 20px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
    transition: border-left-color 0.2s ease;
}
.timeline-record:hover {
    border-left-color: #0284c7;
}

/* Emergency Card */
.emergency-banner {
    background: linear-gradient(135deg, #991b1b 0%, #b91c1c 100%);
    color: white;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 8px 20px rgba(153, 27, 27, 0.25);
    margin: 16px 0;
}
.emergency-banner h2 { color: white !important; margin-top: 0; }
.emergency-banner table { width: 100%; color: white; border-collapse: collapse; }
.emergency-banner td { padding: 8px; vertical-align: top; }

/* Notice Box */
.clinical-notice {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.85rem;
    color: #166534;
    margin: 10px 0;
}
.security-notice {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #64748b;
    margin-top: 14px;
}
</style>
""", unsafe_allow_html=True)

# ── Database Initialization ─────────────────────────────────────────────
db.create_database()
db.add_demo_data()

# ── Session State Management ────────────────────────────────────────────
for key, default in [
    ("logged_in", False),
    ("user_id", None),
    ("username", None),
    ("role", None),
    ("hosp_page", "Dashboard"),
    ("pat_page", "Profile"),
    ("admin_page", "Dashboard"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Navigation Helper ───────────────────────────────────────────────────
def _nav_button(label, page_key, state_key):
    """Renders a styled sidebar button that manages active navigation page."""
    active = st.session_state.get(state_key) == page_key
    icon_prefix = "● " if active else "  "
    if st.sidebar.button(f"{icon_prefix}{label}", key=f"nav_{state_key}_{page_key}"):
        st.session_state[state_key] = page_key
        st.rerun()


# ════════════════════════════════════════════════════════════════════════
# 1. LOGIN & REGISTRATION INTERFACE
# ════════════════════════════════════════════════════════════════════════

def login_page():
    col_l, col_main, col_r = st.columns([1, 2.2, 1])

    with col_main:
        # Professional Application Header
        st.markdown("""
        <div style="text-align: center; padding: 24px 0 16px 0;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: #0f2942; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(15, 41, 66, 0.15);">
                <span style="font-size: 28px; color: #38bdf8;">✚</span>
            </div>
            <h1 style="color: #0f2942; font-size: 2.3rem; margin: 0; font-weight: 800; letter-spacing: -0.5px;">MEDI TIMELINE</h1>
            <p style="color: #0d9488; font-size: 1rem; font-weight: 600; margin: 4px 0 2px 0;">AI-Powered Medical History Intelligence & Secure Patient Record System</p>
            <p style="color: #64748b; font-size: 0.88rem; margin: 0;">Comprehensive Longitudinal Electronic Health Records with Role-Based Consent</p>
        </div>
        """, unsafe_allow_html=True)

        role_tab = st.radio(
            "Access Portal",
            ["Administrator", "Healthcare Facility", "Patient Portal"],
            horizontal=True,
            key="login_role_select",
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # ── 1.1 ADMIN LOGIN ───────────────────────────────────────────
        if role_tab == "Administrator":
            with st.container():
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #0f2942; border-radius: 10px; padding: 22px 24px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);">
                    <h3 style="color: #0f2942; margin-top: 0; font-size: 1.15rem;">System Administration Sign In</h3>
                    <p style="color: #64748b; font-size: 0.85rem; margin-top: -6px; margin-bottom: 16px;">
                        Authorized operational access for system monitoring, facility approvals, and security auditing.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                with st.form("admin_login_form"):
                    username = st.text_input("Username", placeholder="admin", key="adm_u_input")
                    password = st.text_input("Password", type="password", placeholder="Enter password", key="adm_p_input")
                    submit = st.form_submit_button("Sign In to Administrator Console", type="primary", use_container_width=True)

                    if submit:
                        if not username or not password:
                            st.error("Please provide both username and password.")
                        else:
                            user = db.authenticate_user(username)
                            if user and auth.verify_password(password, user[1]):
                                if user[2] != "Admin":
                                    st.error("Access restricted: This account does not possess Administrator authorization.")
                                elif user[3] == 0:
                                    st.error("Account deactivated: Please contact IT security.")
                                else:
                                    auth.login(user[0], username, user[2])
                                    db.add_audit_log(user[0], "Admin", "Admin logged in")
                                    st.success("Authentication successful.")
                                    st.rerun()
                            else:
                                st.error("Authentication failed: Invalid credentials.")

        # ── 1.2 HOSPITAL LOGIN & REGISTRATION ─────────────────────────
        elif role_tab == "Healthcare Facility":
            tab_login, tab_register = st.tabs(["Facility Sign In", "Register New Hospital"])

            with tab_login:
                with st.container():
                    st.markdown("""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #0d9488; border-radius: 10px; padding: 22px 24px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);">
                        <h3 style="color: #0f2942; margin-top: 0; font-size: 1.15rem;">Hospital & Healthcare Provider Sign In</h3>
                        <p style="color: #64748b; font-size: 0.85rem; margin-top: -6px; margin-bottom: 16px;">
                            Access patient charts, record clinical consultations, and review patient health intelligence.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.form("hosp_login_form"):
                        h_username = st.text_input("Hospital Username", placeholder="e.g. cityhospital", key="hl_user")
                        h_password = st.text_input("Password", type="password", placeholder="Enter password", key="hl_pass")
                        h_submit = st.form_submit_button("Sign In to Clinical Workspace", type="primary", use_container_width=True)

                        if h_submit:
                            if not h_username or not h_password:
                                st.error("Please enter credentials.")
                            else:
                                user = db.authenticate_user(h_username)
                                if user and auth.verify_password(h_password, user[1]):
                                    if user[2] != "Hospital":
                                        st.error("Account mismatch: Credentials belong to a non-hospital role.")
                                    elif user[3] == 0:
                                        st.error("Hospital account is disabled. Please contact administrator.")
                                    else:
                                        status = db.get_hospital_approval_status(user[0])
                                        if status == "Pending":
                                            st.warning("Registration Pending: Your facility account is awaiting Administrative approval.")
                                        elif status == "Rejected":
                                            st.error("Registration Status: Facility registration was rejected. Please contact administrator.")
                                        elif status == "Approved":
                                            auth.login(user[0], h_username, user[2])
                                            db.add_audit_log(user[0], "Hospital", "Hospital logged in")
                                            st.success("Welcome!")
                                            st.rerun()
                                        else:
                                            st.error("Hospital account status unresolved. Contact administrator.")
                                else:
                                    st.error("Authentication failed: Invalid credentials.")

            with tab_register:
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #0284c7; border-radius: 10px; padding: 22px 24px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);">
                    <h3 style="color: #0f2942; margin-top: 0; font-size: 1.15rem;">Healthcare Facility Registration</h3>
                    <p style="color: #64748b; font-size: 0.85rem; margin-top: -6px; margin-bottom: 16px;">
                        Register your clinical facility. Submitted registrations undergo administrative verification before activation.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                with st.form("hosp_register_form"):
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        r_hosp_name = st.text_input("Hospital / Facility Name *", placeholder="Apex General Hospital", key="rh_name")
                        r_hosp_code = st.text_input("Facility ID / Registration Code *", placeholder="APEX-HOSP-01", key="rh_code")
                        r_email = st.text_input("Official Facility Email *", placeholder="admin@apexgeneral.com", key="rh_email")
                        r_phone = st.text_input("Contact Phone Number *", placeholder="+91 98765 43210", key="rh_phone")
                    with col_h2:
                        r_doctor = st.text_input("Authorized Chief Medical Officer / Doctor *", placeholder="Dr. S. Sharma, MD", key="rh_doc")
                        r_address = st.text_input("Facility Address *", placeholder="Sector 4, Healthcare City", key="rh_addr")
                        r_username = st.text_input("Desired Login Username *", placeholder="apex_general", key="rh_user")
                        r_pass = st.text_input("Account Password *", type="password", key="rh_pass")
                        r_pass2 = st.text_input("Confirm Account Password *", type="password", key="rh_pass2")

                    r_submit = st.form_submit_button("Submit Facility Registration", type="primary", use_container_width=True)

                    if r_submit:
                        errors = []
                        if not r_hosp_name: errors.append("Hospital Name is required.")
                        if not r_hosp_code: errors.append("Facility Registration Code is required.")
                        if not r_email or "@" not in r_email: errors.append("Valid institutional email is required.")
                        if not r_phone: errors.append("Contact Phone is required.")
                        if not r_address: errors.append("Facility Address is required.")
                        if not r_doctor: errors.append("Authorized Doctor Name is required.")
                        if not r_username: errors.append("Login Username is required.")
                        if not r_pass: errors.append("Password is required.")
                        if r_pass != r_pass2: errors.append("Passwords do not match.")

                        if errors:
                            for e in errors: st.error(e)
                        else:
                            new_uid = db.create_user(r_username, r_pass, "Hospital", r_email)
                            if new_uid:
                                db.register_hospital(new_uid, r_hosp_name, r_hosp_code, r_email, r_phone, r_address, r_doctor)
                                db.add_audit_log(new_uid, "Hospital", "Hospital registered – awaiting verification")
                                st.success("Registration submitted successfully. The account is queued for Administrator verification.")
                            else:
                                st.error("Username already registered. Please choose another username.")

        # ── 1.3 PATIENT LOGIN ─────────────────────────────────────────
        else:
            with st.container():
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #14b8a6; border-radius: 10px; padding: 22px 24px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);">
                    <h3 style="color: #0f2942; margin-top: 0; font-size: 1.15rem;">Patient Health Portal Sign In</h3>
                    <p style="color: #64748b; font-size: 0.85rem; margin-top: -6px; margin-bottom: 16px;">
                        Access your longitudinal medical timeline, emergency medical card, and manage hospital consent requests.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                with st.form("pat_login_form"):
                    p_username = st.text_input("Patient Username", placeholder="e.g. rahul", key="pl_user")
                    p_password = st.text_input("Password", type="password", placeholder="Enter password", key="pl_pass")
                    p_submit = st.form_submit_button("Sign In to Patient Portal", type="primary", use_container_width=True)

                    if p_submit:
                        if not p_username or not p_password:
                            st.error("Please enter credentials.")
                        else:
                            user = db.authenticate_user(p_username)
                            if user and auth.verify_password(p_password, user[1]):
                                if user[2] != "Patient":
                                    st.error("Account mismatch: Credentials belong to a non-patient role.")
                                elif user[3] == 0:
                                    st.error("Patient account deactivated.")
                                else:
                                    auth.login(user[0], p_username, user[2])
                                    db.add_audit_log(user[0], "Patient", "Patient logged in")
                                    st.success("Welcome!")
                                    st.rerun()
                            else:
                                st.error("Authentication failed: Invalid credentials.")

        # Professional Evaluation / Demo Helper Box
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; margin-top: 22px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #0f2942;">System Access Credentials (Evaluation)</span>
                <span class="badge-approved">Active Roles</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; font-size: 0.85rem; color: #334155;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 10px;">
                    <strong style="color: #0f2942;">Administrator:</strong><br>
                    <code>admin</code> / <code>Admin@123</code>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 10px;">
                    <strong style="color: #0d9488;">Hospital:</strong><br>
                    <code>cityhospital</code> / <code>Hospital@123</code>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 10px;">
                    <strong style="color: #0284c7;">Patient:</strong><br>
                    <code>rahul</code> / <code>Patient@123</code>
                </div>
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 8px; text-align: center;">
                Data Security & Integrity: Role-based access control, cryptographic password hashing, and granular patient consent enforced.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# 2. ADMINISTRATOR DASHBOARD
# ════════════════════════════════════════════════════════════════════════

def admin_dashboard():
    # ── Sidebar ───────────────────────────────────────────────────────
    st.sidebar.markdown(f"""
    <div style="padding: 12px 4px 16px 4px; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 12px;">
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #38bdf8; letter-spacing: 0.5px; font-weight: 600;">System Console</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">{st.session_state['username']}</div>
        <div style="font-size: 0.8rem; color: #94a3b8;">Administrator Role</div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("Dashboard Overview", "Dashboard"),
        ("Facility Approvals", "Verification"),
        ("Manage Hospitals", "Hospitals"),
        ("Patient Registry", "Patients"),
        ("Clinical Records", "Records"),
        ("Document Archive", "Documents"),
        ("Security Audit Logs", "AuditLogs"),
    ]
    for label, page in nav_items:
        _nav_button(label, page, "admin_page")

    st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="admin_logout_btn"):
        db.add_audit_log(st.session_state["user_id"], "Admin", "Admin logged out")
        auth.logout()
        st.rerun()

    page = st.session_state.get("admin_page", "Dashboard")

    # ── PAGE: Dashboard Overview ───────────────────────────────────────
    if page == "Dashboard":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Administrative Governance</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">System Administration Dashboard</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Real-time operational metrics across registered clinical institutions, verified patient charts, and audit trails.
            </p>
        </div>
        """, unsafe_allow_html=True)

        stats = db.get_dashboard_statistics()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Registered Hospitals", stats["hospitals"])
        c2.metric("Pending Approvals", stats["pending_hospitals"])
        c3.metric("Approved Facilities", stats["approved_hospitals"])
        c4.metric("Active Patient Charts", stats["patients"])

        c5, c6, c7 = st.columns(3)
        c5.metric("Clinical Records", stats["records"])
        c6.metric("Document Repository", stats["documents"])
        c7.metric("Audit Trail Events", stats["logs"])

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([2, 1])
        with col_act1:
            st.subheader("Recent Security & Operational Audit Log")
            logs_df = db.get_audit_logs(limit=15)
            if not logs_df.empty:
                st.dataframe(
                    logs_df[["timestamp", "username", "role", "action", "medical_id"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No audit entries logged.")

        with col_act2:
            st.subheader("Facility Approvals Queue")
            pending_df = db.get_pending_hospitals()
            if pending_df.empty:
                st.success("No facilities currently awaiting approval.")
            else:
                st.warning(f"**{len(pending_df)}** facility application(s) require review.")
                for _, row in pending_df.head(3).iterrows():
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 3px solid #f59e0b; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                        <strong style="color: #0f2942;">{row.get('hospital_name','N/A')}</strong><br>
                        <span style="font-size: 0.8rem; color: #64748b;">Code: {row.get('hospital_code','N/A')} | Doctor: {row.get('authorized_doctor','N/A')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                if st.button("Review Pending Approvals", key="adm_quick_verify_btn"):
                    st.session_state["admin_page"] = "Verification"
                    st.rerun()

    # ── PAGE: Facility Approvals ───────────────────────────────────────
    elif page == "Verification":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Verification Queue</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Hospital Registration Verification</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Validate credentials, medical authority, and approve or reject hospital registration requests.
            </p>
        </div>
        """, unsafe_allow_html=True)

        pending_df = db.get_pending_hospitals()

        if pending_df.empty:
            st.success("All healthcare facility registration requests have been processed. Zero pending applications.")
        else:
            st.warning(f"**{len(pending_df)} Healthcare Facility Application(s) Awaiting Review**")

            for _, row in pending_df.iterrows():
                h_id = row["hospital_id"]
                with st.expander(
                    f"🏥 {row.get('hospital_name','N/A')} — ID: {row.get('hospital_code','N/A')} — Registered: {str(row.get('created_at',''))[:10]}",
                    expanded=True
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Facility Name:** {row.get('hospital_name','N/A')}")
                        st.write(f"**Facility Code:** `{row.get('hospital_code','N/A')}`")
                        st.write(f"**Official Email:** {row.get('email','N/A')}")
                        st.write(f"**Phone Number:** {row.get('phone','N/A')}")
                    with col2:
                        st.write(f"**Campus Address:** {row.get('address','N/A')}")
                        st.write(f"**Chief Doctor / Medical Officer:** {row.get('authorized_doctor','N/A')}")
                        st.write(f"**System Username:** `{row.get('username','N/A')}`")
                        st.write(f"**Submission Date:** {str(row.get('created_at','N/A'))[:10]}")

                    b_col1, b_col2, _ = st.columns([1.2, 1.2, 3])
                    if b_col1.button("Approve Facility", key=f"adm_approve_{h_id}", type="primary"):
                        db.approve_hospital(h_id)
                        db.add_audit_log(
                            st.session_state["user_id"], "Admin",
                            f"Approved hospital registration: {row.get('hospital_name')}",
                            hospital_id=str(h_id)
                        )
                        st.success(f"Hospital '{row.get('hospital_name')}' has been approved and activated.")
                        st.rerun()

                    if b_col2.button("Reject Application", key=f"adm_reject_{h_id}"):
                        db.reject_hospital(h_id)
                        db.add_audit_log(
                            st.session_state["user_id"], "Admin",
                            f"Rejected hospital registration: {row.get('hospital_name')}",
                            hospital_id=str(h_id)
                        )
                        st.error(f"Hospital '{row.get('hospital_name')}' application rejected.")
                        st.rerun()

    # ── PAGE: Manage Hospitals ────────────────────────────────────────
    elif page == "Hospitals":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Facility Governance</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Healthcare Facility Management</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Directory of registered healthcare providers, approval state control, and facility profile management.
            </p>
        </div>
        """, unsafe_allow_html=True)

        all_hosp = db.get_all_hospitals()
        if all_hosp.empty:
            st.info("No healthcare facilities registered in the database.")
        else:
            filter_status = st.selectbox(
                "Filter Directory by Approval Status",
                ["All Facilities", "Approved", "Pending", "Rejected"],
                key="adm_hosp_filter"
            )
            display_df = all_hosp if filter_status == "All Facilities" else all_hosp[all_hosp["status"] == filter_status]

            st.dataframe(
                display_df[["hospital_id", "hospital_name", "hospital_code", "email", "phone",
                            "authorized_doctor", "status", "created_at", "username", "user_active"]],
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")
            st.subheader("Edit Facility Information")
            h_ids = all_hosp["hospital_id"].tolist()
            h_names = all_hosp["hospital_name"].tolist()
            h_options = [f"{hid} – {hname}" for hid, hname in zip(h_ids, h_names)]
            sel = st.selectbox("Select Healthcare Facility to Edit", h_options, key="adm_edit_hosp_sel")

            if sel:
                sel_id = int(sel.split(" – ")[0])
                sel_row = all_hosp[all_hosp["hospital_id"] == sel_id].iloc[0]

                with st.form("adm_edit_hosp_form"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        e_name = st.text_input("Hospital Name", value=str(sel_row.get("hospital_name", "")))
                        e_email = st.text_input("Official Email", value=str(sel_row.get("email", "")))
                        e_phone = st.text_input("Contact Phone", value=str(sel_row.get("phone", "")))
                    with col_e2:
                        e_addr = st.text_input("Campus Address", value=str(sel_row.get("address", "")))
                        e_doc = st.text_input("Authorized Doctor / Officer", value=str(sel_row.get("authorized_doctor", "")))

                    if st.form_submit_button("Update Facility Record", type="primary"):
                        db.update_hospital(sel_id, e_name, e_email, e_phone, e_addr, e_doc)
                        db.add_audit_log(
                            st.session_state["user_id"], "Admin",
                            f"Updated facility info: {e_name}", hospital_id=str(sel_id)
                        )
                        st.success("Facility details updated successfully.")
                        st.rerun()

                col_toggle, _ = st.columns([2, 3])
                status_desc = "Deactivate" if sel_row.get("user_active", 1) == 1 else "Activate"
                if col_toggle.button(f"{status_desc} Facility Account Access", key=f"adm_toggle_{sel_id}"):
                    db.toggle_hospital_status(sel_id)
                    db.add_audit_log(
                        st.session_state["user_id"], "Admin",
                        f"Toggled hospital active status for ID {sel_id}", hospital_id=str(sel_id)
                    )
                    st.success("Account status toggled.")
                    st.rerun()

    # ── PAGE: Patient Registry ─────────────────────────────────────────
    elif page == "Patients":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Patient Registry</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Master Patient Registry</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Central index of all verified patient electronic health records.
            </p>
        </div>
        """, unsafe_allow_html=True)

        all_pat = db.get_all_patients()
        if all_pat.empty:
            st.info("No patient records registered.")
        else:
            st.dataframe(
                all_pat[["medical_id", "name", "age", "gender", "blood_group", "allergies",
                         "emergency_contact", "phone", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")
            st.subheader("Review Patient Clinical Encounters")
            pat_options = [f"{r['medical_id']} – {r['name']}" for _, r in all_pat.iterrows()]
            sel_pat = st.selectbox("Select Patient Chart", pat_options, key="adm_sel_patient")
            if sel_pat:
                sel_mid = sel_pat.split(" – ")[0]
                hist_df = db.get_history(sel_mid)
                if hist_df.empty:
                    st.info(f"No clinical encounters filed for Medical ID {sel_mid}.")
                else:
                    st.dataframe(hist_df, use_container_width=True, hide_index=True)

    # ── PAGE: Clinical Records ────────────────────────────────────────
    elif page == "Records":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Clinical Repository</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Clinical Encounters & Medical Records</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Consolidated repository of all diagnoses, medications, surgeries, and physician notes.
            </p>
        </div>
        """, unsafe_allow_html=True)

        all_rec = db.get_all_records()
        if all_rec.empty:
            st.info("No medical records entered in the system.")
        else:
            st.write(f"**Total Records Logged:** {len(all_rec)}")
            st.dataframe(all_rec, use_container_width=True, hide_index=True)

    # ── PAGE: Document Archive ────────────────────────────────────────
    elif page == "Documents":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Document Repository</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Clinical Document Archive</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Prescriptions, laboratory panels, discharge summaries, and radiology attachments.
            </p>
        </div>
        """, unsafe_allow_html=True)

        all_docs = db.get_all_documents()
        if all_docs.empty:
            st.info("No documents archived in the repository.")
        else:
            st.dataframe(all_docs, use_container_width=True, hide_index=True)

    # ── PAGE: Security Audit Logs ─────────────────────────────────────
    elif page == "AuditLogs":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Security & Compliance</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Immutable Security Audit Trail</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Comprehensive event timeline tracking user authentication, record access, patient registration, and consent transactions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        logs_df = db.get_audit_logs(limit=500)
        if logs_df.empty:
            st.info("Audit log is empty.")
        else:
            st.write(f"**Total Tracked Events:** {len(logs_df)}")
            st.dataframe(
                logs_df[["timestamp", "username", "role", "action", "medical_id", "hospital_id"]],
                use_container_width=True,
                hide_index=True
            )


# ════════════════════════════════════════════════════════════════════════
# 3. HOSPITAL CLINICAL WORKSPACE
# ════════════════════════════════════════════════════════════════════════

def hospital_dashboard():
    hospital_info = db.get_hospital_by_userid(st.session_state["user_id"])

    if not hospital_info:
        st.error("Hospital profile not found. Please contact Administrator.")
        if st.button("Logout"):
            auth.logout()
            st.rerun()
        return

    h_id = hospital_info["hospital_id"]
    h_name = hospital_info.get("hospital_name", "Hospital")

    # ── Sidebar ───────────────────────────────────────────────────────
    st.sidebar.markdown(f"""
    <div style="padding: 12px 4px 16px 4px; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 12px;">
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #38bdf8; letter-spacing: 0.5px; font-weight: 600;">Clinical Workspace</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">{h_name}</div>
        <div style="font-size: 0.8rem; color: #94a3b8;">Dr: {hospital_info.get('authorized_doctor','N/A')}</div>
        <div style="font-size: 0.75rem; color: #cbd5e1; font-family: monospace;">ID: {hospital_info.get('hospital_code','N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

    hosp_nav_items = [
        ("Workspace Overview", "Dashboard"),
        ("Register New Patient", "RegisterPatient"),
        ("Search Patient & Chart", "SearchPatient"),
        ("Add Medical Record", "AddRecord"),
        ("Clinical AI Summary", "PatientSummary"),
        ("Document OCR Scanner", "OCRScanner"),
        ("Access Requests", "AccessRequests"),
        ("Authorized Patients", "AuthorizedPatients"),
        ("Facility Activity Log", "Activity"),
    ]
    for label, page in hosp_nav_items:
        _nav_button(label, page, "hosp_page")

    st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="hosp_logout_btn"):
        db.add_audit_log(st.session_state["user_id"], "Hospital", "Hospital logged out")
        auth.logout()
        st.rerun()

    page = st.session_state.get("hosp_page", "Dashboard")

    # ── PAGE: Workspace Overview ──────────────────────────────────────
    if page == "Dashboard":
        st.markdown(f"""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Healthcare Facility Workspace</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">{h_name} — Clinical Overview</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Attending Physician: <strong>{hospital_info.get('authorized_doctor','N/A')}</strong> | Facility Code: <code>{hospital_info.get('hospital_code','N/A')}</code>
            </p>
        </div>
        """, unsafe_allow_html=True)

        stats = db.get_hospital_stats(h_id)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Patient Charts", stats["patients"])
        c2.metric("Clinical Records Added", stats["records"])
        c3.metric("Pending Access Requests", stats["pending_requests"])
        c4.metric("Authorized Patients", stats["approved_access"])

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.subheader("Recent Facility Clinical & Consent Activity")
        logs_df = db.get_audit_logs(limit=15)
        hosp_logs = logs_df[logs_df["hospital_id"] == str(h_id)] if not logs_df.empty else pd.DataFrame()
        if hosp_logs.empty:
            st.info("No recent activity recorded for this facility.")
        else:
            st.dataframe(hosp_logs[["timestamp", "action", "medical_id"]], use_container_width=True, hide_index=True)

    # ── PAGE: Register New Patient ────────────────────────────────────
    elif page == "RegisterPatient":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Patient Onboarding</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Register New Patient</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Create a permanent Electronic Medical Record (EMR) account with an automatically generated sequential Medical ID.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("hosp_new_patient_form"):
            col1, col2 = st.columns(2)
            with col1:
                p_name = st.text_input("Patient Full Legal Name *", placeholder="Jane Doe")
                p_dob = st.date_input("Date of Birth *", min_value=date(1900, 1, 1), max_value=date.today())
                p_gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
                p_blood = st.selectbox("Blood Group *", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                p_allergy = st.text_input("Known Allergies & Contraindications", placeholder="e.g. Penicillin, Sulfa drugs, None")
            with col2:
                p_emg = st.text_input("Emergency Contact (Name & Relationship) *", placeholder="John Doe (Spouse)")
                p_phone = st.text_input("Primary Contact Phone *", placeholder="+91 98765 43210")
                p_address = st.text_area("Residential Address *", placeholder="123 Health Boulevard, City")
                p_user = st.text_input("Patient Portal Username *", placeholder="janedoe")
                p_pass = st.text_input("Initial Portal Password *", type="password", placeholder="Enter secure password")

            register = st.form_submit_button("Complete Patient Registration", type="primary", use_container_width=True)

            if register:
                errors = []
                if not p_name: errors.append("Patient full name is required.")
                if not p_emg: errors.append("Emergency contact is required.")
                if not p_phone: errors.append("Phone number is required.")
                if not p_address: errors.append("Residential address is required.")
                if not p_user: errors.append("Patient portal username is required.")
                if not p_pass: errors.append("Initial password is required.")

                if errors:
                    for e in errors: st.error(e)
                else:
                    age = datetime.now().year - p_dob.year
                    med_id = db.generate_medical_id()

                    new_uid = db.create_user(p_user, p_pass, "Patient")
                    if new_uid:
                        db.add_patient(
                            med_id, new_uid, p_name, str(p_dob), age,
                            p_gender, p_blood, p_allergy, p_emg,
                            p_phone, p_address, h_id
                        )
                        # Registering hospital receives pre-approved consent
                        db.request_consent(med_id, h_id, "Registered by this hospital")
                        pending_consents = db.get_hospital_pending_consents(h_id)
                        matching = pending_consents[pending_consents["medical_id"] == med_id]
                        if not matching.empty:
                            db.approve_consent(matching.iloc[0]["consent_id"])

                        db.add_audit_log(
                            st.session_state["user_id"], "Hospital",
                            f"Registered new patient: {p_name}",
                            med_id, str(h_id)
                        )
                        st.success("Patient successfully enrolled into electronic health records.")
                        st.markdown(f"""
                        <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 14px 18px; margin: 12px 0;">
                            <strong style="color: #065f46;">Patient Identifier Assigned:</strong><br>
                            Medical ID: <strong style="font-size: 1.15rem; color: #0f2942;">{med_id}</strong> | Portal Username: <code>{p_user}</code><br>
                            <span style="font-size: 0.85rem; color: #047857;">Clinical consent granted automatically to this hospital.</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Username already registered in patient directory. Choose an alternate username.")

    # ── PAGE: Search Patient & Chart Review ───────────────────────────
    elif page == "SearchPatient":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Clinical Chart Lookup</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Search Patient & Medical History</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Retrieve patient records using their unique Medical ID. Access is strictly protected by patient consent.
            </p>
        </div>
        """, unsafe_allow_html=True)

        search_id = st.text_input(
            "Enter Patient Medical ID",
            placeholder="e.g. MED2026001",
            key="hosp_search_mid"
        )

        if search_id:
            cleaned_mid = search_id.strip().upper()
            patient = db.get_patient(cleaned_mid)

            if patient:
                # Patient Demographics Card
                st.markdown(f"""
                <div class="med-card" style="border-top: 3px solid #0d9488;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b;">Verified Patient Profile</span>
                            <h2 style="color: #0f2942; margin: 2px 0 0 0;">{patient['name']}</h2>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-family: monospace; font-size: 1rem;">
                                {patient['medical_id']}
                            </span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-top: 16px; padding-top: 14px; border-top: 1px solid #e2e8f0;">
                        <div><span style="color: #64748b; font-size: 0.82rem;">Age / Gender:</span><br><strong>{patient['age']} yrs</strong> ({patient['gender']})</div>
                        <div><span style="color: #64748b; font-size: 0.82rem;">Blood Group:</span><br><strong style="color: #dc2626;">{patient['blood_group']}</strong></div>
                        <div><span style="color: #64748b; font-size: 0.82rem;">Allergies:</span><br><strong style="color: #d97706;">{patient['allergies'] or 'None recorded'}</strong></div>
                        <div><span style="color: #64748b; font-size: 0.82rem;">Emergency Contact:</span><br><strong>{patient['emergency_contact']}</strong></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                has_access = db.check_hospital_access(cleaned_mid, h_id)

                if has_access:
                    st.markdown("""
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px;">
                        <span class="badge-approved">Authorized Clinical Access Granted</span>
                        <span style="font-size: 0.82rem; color: #64748b;">Patient has active consent on record.</span>
                    </div>
                    """, unsafe_allow_html=True)

                    db.add_audit_log(
                        st.session_state["user_id"], "Hospital",
                        "Viewed patient medical chart", cleaned_mid, str(h_id)
                    )

                    hist_df = db.get_history(cleaned_mid)

                    st.markdown("### Medical History Timeline & Records")

                    # Date-Range Selector & Event Filter for reviewing medical records
                    col_f1, col_f2 = st.columns([1.5, 1.5])
                    with col_f1:
                        period_filter = st.selectbox(
                            "Review Date Range",
                            ["All Records", "Last 30 Days", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Custom Range"],
                            key="hosp_review_period"
                        )
                    with col_f2:
                        event_types = ["All Types"]
                        if not hist_df.empty and 'event_type' in hist_df.columns:
                            event_types.extend(sorted(hist_df['event_type'].dropna().unique().tolist()))
                        type_filter = st.selectbox("Event Category Filter", event_types, key="hosp_review_type")

                    # Date filtering
                    filtered_df = hist_df.copy()
                    if not filtered_df.empty and 'event_date' in filtered_df.columns:
                        filtered_df['parsed_date'] = pd.to_datetime(filtered_df['event_date'], errors='coerce')

                        if period_filter == "Custom Range":
                            col_c1, col_c2 = st.columns(2)
                            cs_date = col_c1.date_input("Start Date", key="hosp_cust_start")
                            ce_date = col_c2.date_input("End Date", key="hosp_cust_end")
                            filtered_df = filtered_df[
                                (filtered_df['parsed_date'] >= pd.to_datetime(cs_date)) &
                                (filtered_df['parsed_date'] <= pd.to_datetime(ce_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
                            ]
                        elif period_filter != "All Records":
                            s_ts, e_ts = ai_summary.get_date_range(period_filter)
                            if s_ts is not None:
                                filtered_df = filtered_df[filtered_df['parsed_date'] >= s_ts]

                        if type_filter != "All Types":
                            filtered_df = filtered_df[filtered_df['event_type'] == type_filter]

                    if filtered_df.empty:
                        st.info("No medical encounters matching the selected filters.")
                    else:
                        st.write(f"Displaying **{len(filtered_df)}** medical record(s):")

                        tab_card_view, tab_table_view = st.tabs(["Structured Clinical Cards", "Tabular View"])

                        with tab_card_view:
                            for _, rec in filtered_df.iterrows():
                                st.markdown(f"""
                                <div class="timeline-record">
                                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                        <div>
                                            <strong style="color: #0f2942; font-size: 1rem;">{rec.get('event_date','')}</strong>
                                            <span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: 600; margin-left: 8px;">{rec.get('event_type','Clinical Event')}</span>
                                        </div>
                                        <div style="font-size: 0.85rem; color: #64748b;">
                                            {rec.get('hospital_name','')} | Dr. {rec.get('doctor_name','')}
                                        </div>
                                    </div>
                                    <div style="margin-top: 8px; font-size: 0.92rem; color: #1e293b;">
                                        {rec.get('description','')}
                                    </div>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; margin-top: 10px; padding-top: 8px; border-top: 1px dashed #e2e8f0; font-size: 0.85rem;">
                                        {f"<div><strong>Diagnosis:</strong> {rec.get('diagnosis')}</div>" if rec.get('diagnosis') else ""}
                                        {f"<div><strong>Medication:</strong> {rec.get('medicine')}</div>" if rec.get('medicine') else ""}
                                        {f"<div><strong>Test Result:</strong> {rec.get('test_result')}</div>" if rec.get('test_result') else ""}
                                        {f"<div><strong>Surgery:</strong> {rec.get('surgery')}</div>" if rec.get('surgery') else ""}
                                    </div>
                                    {f"<div style='margin-top: 6px; font-size: 0.82rem; color: #64748b;'><em>Notes: {rec.get('notes')}</em></div>" if rec.get('notes') else ""}
                                </div>
                                """, unsafe_allow_html=True)

                        with tab_table_view:
                            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

                else:
                    st.markdown("""
                    <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 14px 18px; margin: 14px 0;">
                        <strong style="color: #92400e; font-size: 1rem;">Restricted Access: Patient Consent Required</strong>
                        <p style="color: #78350f; font-size: 0.88rem; margin: 4px 0 10px 0;">
                            This healthcare facility does not possess active consent to view this patient's medical records.
                            In compliance with healthcare privacy protocols, submit a formal consent request below.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.form("hosp_request_access_form"):
                        reason = st.text_input("Clinical Purpose / Reason for Access Request *", placeholder="e.g. Outpatient consultation and diagnostic evaluation")
                        req_btn = st.form_submit_button("Submit Consent Request to Patient", type="primary")

                        if req_btn:
                            if not reason:
                                st.error("Please provide a clinical reason for the consent request.")
                            else:
                                ok = db.request_consent(cleaned_mid, h_id, reason)
                                if ok:
                                    db.add_audit_log(
                                        st.session_state["user_id"], "Hospital",
                                        "Submitted patient access consent request",
                                        cleaned_mid, str(h_id)
                                    )
                                    st.success("Consent request submitted. The patient can approve access from their portal.")
                                else:
                                    st.info("A pending or approved consent request already exists for this patient chart.")
            else:
                st.error("No patient located with the specified Medical ID. Please verify the ID.")

    # ── PAGE: Add Medical Record ──────────────────────────────────────
    elif page == "AddRecord":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Clinical Entry</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">File Medical Encounter Record</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Log clinical consultations, diagnoses, pharmacotherapy prescriptions, lab results, and procedures.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("hosp_add_record_form"):
            col1, col2 = st.columns(2)
            with col1:
                mid = st.text_input("Patient Medical ID *", placeholder="MED2026001")
                doctor = st.text_input("Attending Physician *", value=hospital_info.get("authorized_doctor", ""))
                rec_date = st.date_input("Consultation Date *", value=date.today())
                rec_type = st.selectbox("Encounter Type *", [
                    "General Consultation", "Specialist Diagnosis", "Emergency Visit",
                    "Hospital Admission", "Discharge Summary", "Surgical Procedure",
                    "Laboratory Test", "Radiology / Imaging", "Vaccination",
                    "Follow-up Consultation", "Chronic Disease Monitoring", "Other"
                ])
                diagnosis = st.text_input("Clinical Diagnosis / Assessment", placeholder="e.g. Essential Hypertension")
            with col2:
                medicine = st.text_input("Prescribed Medications & Dosages", placeholder="e.g. Amlodipine 5mg OD")
                test_result = st.text_input("Diagnostic / Lab Findings", placeholder="e.g. BP 130/85 mmHg")
                surgery = st.text_input("Surgical Intervention (if performed)", placeholder="e.g. None")
                desc = st.text_area("Encounter Summary *", placeholder="Clinical observations and chief complaint")
                notes = st.text_area("Physician Clinical Notes", placeholder="Follow-up instructions and precautions")

            submit_rec = st.form_submit_button("Record Clinical Entry into EMR", type="primary", use_container_width=True)

            if submit_rec:
                if not mid or not doctor or not desc:
                    st.error("Medical ID, Attending Physician, and Encounter Summary are mandatory fields.")
                else:
                    mid_clean = mid.strip().upper()
                    patient = db.get_patient(mid_clean)
                    if not patient:
                        st.error("Patient record not found. Verify the Medical ID.")
                    elif not db.check_hospital_access(mid_clean, h_id):
                        st.error("Access unauthorized: This facility does not possess active consent for this patient. Request consent first.")
                    else:
                        db.add_medical_record(
                            mid_clean, h_id, h_name, doctor,
                            str(rec_date), rec_type, desc,
                            diagnosis, medicine, test_result, surgery, notes
                        )
                        db.add_audit_log(
                            st.session_state["user_id"], "Hospital",
                            f"Added medical record ({rec_type})",
                            mid_clean, str(h_id)
                        )
                        st.success(f"Clinical record successfully added to chart for {patient['name']} (ID: {mid_clean}).")

    # ── PAGE: Patient AI Summary ──────────────────────────────────────
    elif page == "PatientSummary":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Clinical Intelligence</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Clinical Medical History Summary</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Period-based synthesis of patient diagnoses, pharmacotherapy, procedures, and longitudinal care insights.
            </p>
        </div>
        """, unsafe_allow_html=True)

        approved_df = db.get_hospital_approved_consents(h_id)

        if approved_df.empty:
            st.warning("No authorized patient charts available. Submit access requests via Patient Search first.")
        else:
            patient_options = [
                f"{row['medical_id']} – {row['patient_name']}"
                for _, row in approved_df.iterrows()
            ]
            col_s1, col_s2 = st.columns([2, 1.5])
            with col_s1:
                sel_patient = st.selectbox("Select Authorized Patient Chart", patient_options, key="hosp_sum_pat")
            with col_s2:
                period = st.selectbox("Analysis Time Window", [
                    "All Time", "Last 7 Days", "Last 30 Days", "Last 2 Months",
                    "Last 3 Months", "Last 6 Months", "Last 1 Year", "Custom Date Range"
                ], key="hosp_sum_period")

            start_date = end_date = None
            if period == "Custom Date Range":
                col_s, col_e = st.columns(2)
                d_start = col_s.date_input("Start Date", key="hosp_sum_dstart")
                d_end = col_e.date_input("End Date", key="hosp_sum_dend")
                start_date = pd.to_datetime(d_start)
                end_date = pd.to_datetime(d_end)
            else:
                start_date, end_date = ai_summary.get_date_range(period)

            if st.button("Synthesize Clinical Intelligence Summary", key="hosp_gen_sum_btn", type="primary"):
                sel_mid = sel_patient.split(" – ")[0]
                hist_df = db.get_history(sel_mid)
                db.add_audit_log(
                    st.session_state["user_id"], "Hospital",
                    "Generated AI summary", sel_mid, str(h_id)
                )
                summary_content = ai_summary.generate_period_summary(hist_df, start_date, end_date)
                st.markdown(summary_content, unsafe_allow_html=True)

    # ── PAGE: OCR Document Scanner ────────────────────────────────────
    elif page == "OCRScanner":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Document Intake</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Optical Document Intake Scanner</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Digitize paper records, lab sheets, and external referral letters with structured clinician verification.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.info(ocr_module.get_install_message())

        st.subheader("Upload Clinical Document")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            mid_ocr = st.text_input("Patient Medical ID *", placeholder="MED2026001", key="ocr_mid")
        with col_u2:
            doc_type = st.selectbox("Document Classification", [
                "Prescription Order", "Laboratory Report", "Discharge Summary",
                "Clinical Consultant Letter", "Diagnostic Scan / Imaging", "Other"
            ], key="ocr_doctype")

        uploaded_file = st.file_uploader(
            "Select Document (PDF, PNG, JPG, JPEG)",
            type=["pdf", "png", "jpg", "jpeg"],
            key="ocr_uploader"
        )

        if uploaded_file is not None:
            st.success(f"Attached file: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

            if st.button("Process Document & Extract Fields", key="ocr_extract_btn", type="primary"):
                with st.spinner("Processing document..."):
                    extracted_text = ocr_module.extract_text(uploaded_file)
                    parsed = ocr_module.parse_medical_fields(extracted_text)
                    st.session_state["ocr_extracted"] = extracted_text
                    st.session_state["ocr_parsed"] = parsed

            parsed = st.session_state.get("ocr_parsed", {})
            extracted_text = st.session_state.get("ocr_extracted", "")

            st.markdown("---")
            st.subheader("Clinician Verification & Chart Entry")
            st.markdown("""
            <div class="security-notice">
                <strong>Clinician Verification Requirement:</strong> Review all parsed clinical fields carefully against the uploaded document prior to committing records to the patient's permanent EMR.
            </div>
            """, unsafe_allow_html=True)

            with st.form("ocr_confirm_form"):
                col1, col2 = st.columns(2)
                with col1:
                    ocr_doctor = st.text_input("Attending Physician", value=hospital_info.get("authorized_doctor", ""), key="ocr_f_doctor")
                    ocr_date = st.text_input("Record Date", value=str(date.today()), key="ocr_f_date")
                    ocr_diag = st.text_input("Extracted Diagnosis", value=parsed.get("diagnosis", ""), key="ocr_f_diag")
                    ocr_med = st.text_input("Prescribed Medications", value=parsed.get("medicine", ""), key="ocr_f_med")
                with col2:
                    ocr_test = st.text_input("Extracted Lab / Diagnostic Findings", value=parsed.get("test_result", ""), key="ocr_f_test")
                    ocr_surg = st.text_input("Surgical Procedures (if noted)", value=parsed.get("surgery", ""), key="ocr_f_surg")
                    ocr_desc = st.text_area("Encounter Description", value=f"{doc_type} processed via optical scanner", key="ocr_f_desc")

                confirm_btn = st.form_submit_button("Verify & Commit to Patient Record", type="primary", use_container_width=True)

                if confirm_btn:
                    if not mid_ocr:
                        st.error("Patient Medical ID is required.")
                    else:
                        mid_clean = mid_ocr.strip().upper()
                        patient = db.get_patient(mid_clean)
                        if not patient:
                            st.error("Patient not found in registry.")
                        elif not db.check_hospital_access(mid_clean, h_id):
                            st.error("No active consent for this patient chart.")
                        else:
                            os.makedirs("uploads", exist_ok=True)
                            file_path = os.path.join("uploads", uploaded_file.name)
                            try:
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                            except Exception:
                                pass

                            db.save_document(mid_clean, h_id, doc_type, uploaded_file.name, file_path, extracted_text)
                            try:
                                rec_date = pd.to_datetime(ocr_date).date()
                            except Exception:
                                rec_date = date.today()

                            db.add_medical_record(
                                mid_clean, h_id, h_name, ocr_doctor,
                                str(rec_date), doc_type, ocr_desc,
                                ocr_diag, ocr_med, ocr_test, ocr_surg,
                                "Verified intake from uploaded clinical document"
                            )
                            db.add_audit_log(
                                st.session_state["user_id"], "Hospital",
                                "OCR document uploaded and verified",
                                mid_clean, str(h_id)
                            )
                            st.success("Document verified and clinical record saved successfully.")
                            st.session_state["ocr_extracted"] = ""
                            st.session_state["ocr_parsed"] = {}

    # ── PAGE: Access Requests ──────────────────────────────────────────
    elif page == "AccessRequests":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Consent Governance</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Patient Consent & Access Governance</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Track access consent requests submitted to patients and monitor authorization states.
            </p>
        </div>
        """, unsafe_allow_html=True)

        pending_df = db.get_hospital_pending_consents(h_id)
        st.subheader("Pending Patient Consent Requests")
        if pending_df.empty:
            st.info("No pending access requests awaiting patient action.")
        else:
            for _, row in pending_df.iterrows():
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 3px solid #f59e0b; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #0f2942; font-size: 1rem;">{row.get('patient_name','N/A')}</strong>
                        <span class="badge-pending">Pending Patient Approval</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; margin-top: 4px;">
                        Medical ID: <code>{row.get('medical_id','N/A')}</code> | Requested: {str(row.get('requested_at',''))[:16]}
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">
                        Purpose: <em>{row.get('reason','N/A')}</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Active Authorized Consents")
        all_req_df = db.get_hospital_approved_consents(h_id)
        if all_req_df.empty:
            st.info("No active authorized patient consents.")
        else:
            st.dataframe(
                all_req_df[["medical_id", "patient_name", "status", "approved_at"]],
                use_container_width=True,
                hide_index=True
            )

    # ── PAGE: Authorized Patients ──────────────────────────────────────
    elif page == "AuthorizedPatients":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Authorized Charts</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Active Authorized Patients Directory</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Patients who have explicitly authorized this healthcare facility to view and manage their medical records.
            </p>
        </div>
        """, unsafe_allow_html=True)

        auth_df = db.get_hospital_approved_consents(h_id)
        if auth_df.empty:
            st.info("No authorized patients currently registered.")
        else:
            st.dataframe(
                auth_df[["medical_id", "patient_name", "approved_at"]],
                use_container_width=True,
                hide_index=True
            )

    # ── PAGE: Activity ─────────────────────────────────────────────────
    elif page == "Activity":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Facility Audit Trail</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Facility Clinical Activity Log</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Chronological record of all actions initiated from this healthcare facility account.
            </p>
        </div>
        """, unsafe_allow_html=True)

        logs_df = db.get_audit_logs(limit=200)
        if not logs_df.empty:
            hosp_logs = logs_df[(logs_df["hospital_id"] == str(h_id)) | (logs_df["role"] == "Hospital")]
            if hosp_logs.empty:
                st.info("No activity records available.")
            else:
                st.dataframe(
                    hosp_logs[["timestamp", "username", "action", "medical_id"]],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No activity recorded yet.")


# ════════════════════════════════════════════════════════════════════════
# 4. PATIENT HEALTH PORTAL
# ════════════════════════════════════════════════════════════════════════

def patient_dashboard():
    patient = db.get_patient_by_userid(st.session_state["user_id"])

    if not patient:
        st.error("Patient profile not found. Please contact your registering healthcare facility.")
        if st.button("Logout", key="pat_no_profile_logout"):
            auth.logout()
            st.rerun()
        return

    m_id = patient["medical_id"]
    p_name = patient["name"]

    # ── Sidebar ───────────────────────────────────────────────────────
    st.sidebar.markdown(f"""
    <div style="padding: 12px 4px 16px 4px; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 12px;">
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #38bdf8; letter-spacing: 0.5px; font-weight: 600;">Patient Portal</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">{p_name}</div>
        <div style="font-size: 0.8rem; color: #94a3b8; font-family: monospace;">ID: {m_id}</div>
        <div style="font-size: 0.75rem; color: #f87171; font-weight: 600; margin-top: 2px;">Blood: {patient.get('blood_group','N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

    pat_nav_items = [
        ("My Health Profile", "Profile"),
        ("Medical Timeline", "Timeline"),
        ("Health Intelligence Summary", "AISummary"),
        ("Emergency Medical Card", "EmergencyCard"),
        ("Hospital Permissions", "Permissions"),
    ]
    for label, page in pat_nav_items:
        _nav_button(label, page, "pat_page")

    st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="pat_logout_btn"):
        db.add_audit_log(st.session_state["user_id"], "Patient", "Patient logged out")
        auth.logout()
        st.rerun()

    page = st.session_state.get("pat_page", "Profile")

    # ── PAGE: Profile ─────────────────────────────────────────────────
    if page == "Profile":
        st.markdown(f"""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Personal Health Record</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Welcome, {p_name}</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Unique Medical ID: <code style="color: #ffffff; background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px;">{m_id}</code>
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Vital Demographics")
            c1, c2, c3 = st.columns(3)
            c1.metric("Age", f"{patient.get('age', 'N/A')} yrs")
            c2.metric("Gender", patient.get('gender', 'N/A'))
            c3.metric("Blood Group", patient.get('blood_group', 'N/A'))

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="med-card">
                <h4 style="color: #0f2942; margin-top: 0;">Detailed Patient Profile</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; font-size: 0.9rem;">
                    <div><span style="color: #64748b;">Date of Birth:</span><br><strong>{patient.get('date_of_birth', 'N/A')}</strong></div>
                    <div><span style="color: #64748b;">Primary Phone:</span><br><strong>{patient.get('phone', 'N/A')}</strong></div>
                    <div><span style="color: #64748b;">Allergies & Contraindications:</span><br><strong style="color: #d97706;">{patient.get('allergies', 'None recorded')}</strong></div>
                    <div><span style="color: #64748b;">Emergency Contact:</span><br><strong style="color: #dc2626;">{patient.get('emergency_contact', 'N/A')}</strong></div>
                </div>
                <div style="margin-top: 14px; font-size: 0.9rem;">
                    <span style="color: #64748b;">Residential Address:</span><br>
                    <strong>{patient.get('address', 'N/A')}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("Patient Safety Alert")
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #dc2626; border-radius: 10px; padding: 18px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
                <div style="font-size: 0.8rem; text-transform: uppercase; color: #dc2626; font-weight: 700; letter-spacing: 0.5px;">Emergency Indicators</div>
                <div style="margin-top: 10px; font-size: 0.9rem;">
                    <span style="color: #64748b;">Blood Type:</span> <strong style="font-size: 1.1rem; color: #0f2942;">{patient.get('blood_group','N/A')}</strong><br>
                    <span style="color: #64748b;">Active Allergies:</span> <strong style="color: #b91c1c;">{patient.get('allergies','None known')}</strong><br>
                    <span style="color: #64748b;">Emergency Phone:</span> <strong>{patient.get('emergency_contact','N/A')}</strong>
                </div>
            </div>
            <div class="security-notice">
                <strong>Data Privacy Assurance:</strong> Your electronic medical history is protected by role-based authorization. Hospitals cannot access your records without your explicit approval.
            </div>
            """, unsafe_allow_html=True)

    # ── PAGE: Medical Timeline ────────────────────────────────────────
    elif page == "Timeline":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Longitudinal Health History</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">My Medical Timeline</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Chronological record of verified clinical encounters, consultations, diagnoses, and prescriptions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Clear clinical transparency notice
        st.markdown("""
        <div class="clinical-notice">
            <strong>Verified Clinical Record:</strong> Entries below are documented by attending physicians and hospitals during your medical visits. Patient accounts have read-only access to preserve clinical audit integrity.
        </div>
        """, unsafe_allow_html=True)

        hist_df = db.get_history(m_id)

        if hist_df.empty:
            st.info("No clinical records currently filed for your Medical ID.")
        else:
            # Filtering options
            col_t1, col_t2 = st.columns([1.5, 1.5])
            with col_t1:
                period_filter = st.selectbox(
                    "Filter Time Window",
                    ["All Records", "Last 30 Days", "Last 6 Months", "Last 1 Year"],
                    key="pat_time_period"
                )
            with col_t2:
                rec_types = ["All Record Types"]
                if 'event_type' in hist_df.columns:
                    rec_types.extend(sorted(hist_df['event_type'].dropna().unique().tolist()))
                type_filter = st.selectbox("Filter by Record Category", rec_types, key="pat_time_type")

            # Apply filters
            sorted_df = hist_df.copy()
            if 'event_date' in sorted_df.columns:
                sorted_df['parsed_date'] = pd.to_datetime(sorted_df['event_date'], errors='coerce')
                if period_filter != "All Records":
                    s_ts, _ = ai_summary.get_date_range(period_filter)
                    if s_ts is not None:
                        sorted_df = sorted_df[sorted_df['parsed_date'] >= s_ts]

                if type_filter != "All Record Types":
                    sorted_df = sorted_df[sorted_df['event_type'] == type_filter]

                sorted_df = sorted_df.sort_values(by='parsed_date', ascending=False)
                sorted_df['year'] = sorted_df['parsed_date'].dt.year

            if sorted_df.empty:
                st.info("No records found matching the selected filter criteria.")
            else:
                years = sorted_df['year'].dropna().unique()
                for year in sorted(years, reverse=True):
                    st.markdown(f"""
                    <div style="margin: 20px 0 10px 0; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.15rem; font-weight: 700; color: #0f2942;">Year {int(year)}</span>
                        <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
                    </div>
                    """, unsafe_allow_html=True)

                    year_df = sorted_df[sorted_df['year'] == year]

                    for _, row in year_df.iterrows():
                        etype = row.get('event_type', 'Clinical Visit')
                        desc = row.get('description', '')
                        diag = row.get('diagnosis', '')
                        doctor = row.get('doctor_name', '')
                        hosp = row.get('hospital_name', '')
                        med = row.get('medicine', '')
                        test = row.get('test_result', '')
                        surg = row.get('surgery', '')
                        notes = row.get('notes', '')

                        st.markdown(f"""
                        <div class="timeline-record">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <div>
                                    <strong style="color: #0f2942; font-size: 1rem;">{row.get('event_date','')}</strong>
                                    <span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: 600; margin-left: 8px;">{etype}</span>
                                </div>
                                <div style="font-size: 0.85rem; color: #64748b;">
                                    {hosp} | Dr. {doctor}
                                </div>
                            </div>
                            <div style="margin-top: 8px; font-size: 0.92rem; color: #1e293b;">
                                {desc}
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; margin-top: 10px; padding-top: 8px; border-top: 1px dashed #e2e8f0; font-size: 0.85rem;">
                                {f"<div><span style='color:#64748b;'>Diagnosis:</span> <strong style='color:#0f2942;'>{diag}</strong></div>" if diag else ""}
                                {f"<div><span style='color:#64748b;'>Medication:</span> <strong style='color:#0284c7;'>{med}</strong></div>" if med else ""}
                                {f"<div><span style='color:#64748b;'>Findings:</span> {test}</div>" if test else ""}
                                {f"<div><span style='color:#64748b;'>Procedure:</span> <strong style='color:#6366f1;'>{surg}</strong></div>" if surg else ""}
                            </div>
                            {f"<div style='margin-top: 6px; font-size: 0.82rem; color: #64748b;'><em>Notes: {notes}</em></div>" if notes else ""}
                        </div>
                        """, unsafe_allow_html=True)

    # ── PAGE: AI Summary ──────────────────────────────────────────────
    elif page == "AISummary":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Personal Health Intelligence</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Clinical Health Summary & Intelligence</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Comprehensive structured overview synthesizing diagnoses, medications, procedures, and health guidelines.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_p1, _ = st.columns([2, 2])
        with col_p1:
            period = st.selectbox("Select History Period for Analysis", [
                "All Time", "Last 30 Days", "Last 2 Months",
                "Last 3 Months", "Last 6 Months", "Last 1 Year", "Custom Date Range"
            ], key="pat_ai_period")

        start_date = end_date = None
        if period == "Custom Date Range":
            col_s, col_e = st.columns(2)
            d_start = col_s.date_input("Start Date", key="pat_dstart")
            d_end = col_e.date_input("End Date", key="pat_dend")
            start_date = pd.to_datetime(d_start)
            end_date = pd.to_datetime(d_end)
        else:
            start_date, end_date = ai_summary.get_date_range(period)

        if st.button("Generate Health Intelligence Summary", key="pat_gen_sum_btn", type="primary"):
            hist_df = db.get_history(m_id)
            db.add_audit_log(
                st.session_state["user_id"], "Patient",
                "Generated personal health summary", m_id
            )
            summary_content = ai_summary.generate_period_summary(hist_df, start_date, end_date)
            st.markdown(summary_content, unsafe_allow_html=True)

    # ── PAGE: Emergency Card ──────────────────────────────────────────
    elif page == "EmergencyCard":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Emergency Response</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Emergency Medical Alert Card</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                Rapid clinical reference card for first responders and emergency room physicians during critical care triage.
            </p>
        </div>
        """, unsafe_allow_html=True)

        hist_df = db.get_history(m_id)

        major_diagnoses = []
        major_surgeries = []
        current_medicines = []

        if not hist_df.empty:
            diag_series = hist_df['diagnosis'].dropna()
            for d in diag_series:
                d = str(d).strip()
                if d and d.lower() not in ['', 'none', 'n/a', 'healthy birth, no complications', 'clear – no abnormality']:
                    if d not in major_diagnoses:
                        major_diagnoses.append(d)

            if 'surgery' in hist_df.columns:
                surg_series = hist_df['surgery'].dropna()
                for s in surg_series:
                    s = str(s).strip()
                    if s and s.lower() not in ['', 'none', 'n/a']:
                        if s not in major_surgeries:
                            major_surgeries.append(s)

            recent_df = hist_df.head(5)
            med_series = recent_df['medicine'].dropna()
            for med in med_series:
                med = str(med).strip()
                if med and med.lower() not in ['', 'none', 'n/a']:
                    if med not in current_medicines:
                        current_medicines.append(med)

        diag_str = "<br>".join([f"• {d}" for d in major_diagnoses]) if major_diagnoses else "• None recorded"
        surg_str = "<br>".join([f"• {s}" for s in major_surgeries]) if major_surgeries else "• None recorded"
        med_str = "<br>".join([f"• {m}" for m in current_medicines]) if current_medicines else "• None recorded"

        st.markdown(f"""
        <div class="emergency-banner">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.25); padding-bottom: 12px; margin-bottom: 16px;">
                <div>
                    <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #fecaca; font-weight: 700;">Critical Care Alert</span>
                    <h2 style="margin: 0; font-size: 1.6rem;">EMERGENCY MEDICAL PROFILE</h2>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 8px; font-family: monospace; font-size: 1.1rem; font-weight: 700;">
                    {m_id}
                </div>
            </div>

            <table>
                <tr>
                    <td style="width: 50%;">
                        <span style="color: #fecaca; font-size: 0.8rem; text-transform: uppercase;">Patient Name</span><br>
                        <strong style="font-size: 1.3rem;">{patient.get('name','N/A')}</strong>
                    </td>
                    <td style="width: 50%;">
                        <span style="color: #fecaca; font-size: 0.8rem; text-transform: uppercase;">Blood Group</span><br>
                        <strong style="font-size: 1.6rem; color: #ffffff;">{patient.get('blood_group','N/A')}</strong>
                    </td>
                </tr>
                <tr>
                    <td>
                        <span style="color: #fecaca; font-size: 0.8rem; text-transform: uppercase;">Known Allergies</span><br>
                        <strong style="font-size: 1rem; color: #ffedd5;">{patient.get('allergies','None recorded')}</strong>
                    </td>
                    <td>
                        <span style="color: #fecaca; font-size: 0.8rem; text-transform: uppercase;">Primary Emergency Contact</span><br>
                        <strong style="font-size: 1rem;">{patient.get('emergency_contact','N/A')} ({patient.get('phone','')})</strong>
                    </td>
                </tr>
                <tr>
                    <td>
                        <span style="color: #fecaca; font-size: 0.8rem; text-transform: uppercase;">Major Diagnosed Conditions</span><br>
                        <div style="font-size: 0.88rem; margin-top: 4px; color: #fffbeb;">{diag_str}</div>
                    </td>
                    <td>
                        <span style="color: #fecaca; font-size: 0.8rem; text-transform: uppercase;">Surgical Procedures</span><br>
                        <div style="font-size: 0.88rem; margin-top: 4px; color: #fffbeb;">{surg_str}</div>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        <span style="color: #fecaca; font-size: 0.8rem; text-transform: uppercase;">Active / Recent Prescriptions</span><br>
                        <div style="font-size: 0.88rem; margin-top: 4px; color: #ecfdf5;">{med_str}</div>
                    </td>
                </tr>
            </table>

            <div style="border-top: 1px solid rgba(255,255,255,0.25); margin-top: 16px; padding-top: 10px; font-size: 0.75rem; color: #fecaca;">
                Medical Alert Notice: Synthesized from recorded electronic health profile. Cross-verify with active clinical records during emergency intake. In acute emergencies, contact Emergency Medical Services (EMS) immediately.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── PAGE: Access Permissions ──────────────────────────────────────
    elif page == "Permissions":
        st.markdown("""
        <div class="med-header-card">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Consent Governance</div>
            <h1 style="color: white; margin: 4px 0 0 0; font-size: 1.7rem;">Hospital Access Permissions</h1>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 6px 0 0 0;">
                You retain complete governance over which hospitals and clinicians can view your longitudinal health records.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Pending Hospital Access Requests")
        req_df = db.get_pending_requests(m_id)

        if req_df.empty:
            st.info("No pending access requests from hospitals.")
        else:
            for _, row in req_df.iterrows():
                with st.container():
                    col_a, col_b, col_c = st.columns([4, 1.2, 1.2])
                    col_a.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 3px solid #f59e0b; border-radius: 8px; padding: 12px 16px;">
                        <strong style="color: #0f2942; font-size: 1rem;">🏥 {row.get('hospital_name','N/A')}</strong><br>
                        <span style="font-size: 0.85rem; color: #475569;">Purpose: <em>{row.get('reason','N/A')}</em></span><br>
                        <span style="font-size: 0.78rem; color: #94a3b8;">Requested: {str(row.get('requested_at',''))[:16]}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if col_b.button("Grant Access", key=f"pat_app_{row['consent_id']}", type="primary"):
                        db.approve_consent(row["consent_id"])
                        db.add_audit_log(
                            st.session_state["user_id"], "Patient",
                            f"Approved hospital access: {row.get('hospital_name')}",
                            m_id
                        )
                        st.success(f"Access granted to {row.get('hospital_name')}.")
                        st.rerun()

                    if col_c.button("Deny Request", key=f"pat_rej_{row['consent_id']}"):
                        db.reject_consent(row["consent_id"])
                        db.add_audit_log(
                            st.session_state["user_id"], "Patient",
                            f"Rejected hospital access: {row.get('hospital_name')}",
                            m_id
                        )
                        st.error(f"Access request denied.")
                        st.rerun()

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Currently Authorized Healthcare Facilities")
        app_df = db.get_patient_consents(m_id)

        if app_df.empty:
            st.info("No healthcare facilities currently possess authorized access to your records.")
        else:
            for _, row in app_df.iterrows():
                col_a, col_b = st.columns([5, 1.5])
                col_a.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 3px solid #0d9488; border-radius: 8px; padding: 12px 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #0f2942; font-size: 1rem;">🏥 {row.get('hospital_name','N/A')}</strong>
                        <span class="badge-approved">Active Authorization</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                        Approved On: {str(row.get('approved_at',''))[:16]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if col_b.button("Revoke Access", key=f"pat_rev_{row['consent_id']}"):
                    db.revoke_consent(m_id, row["hospital_id"])
                    db.add_audit_log(
                        st.session_state["user_id"], "Patient",
                        f"Revoked hospital access: {row.get('hospital_name')}",
                        m_id
                    )
                    st.warning(f"Access revoked for {row.get('hospital_name')}.")
                    st.rerun()

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# 5. MAIN ROUTER
# ════════════════════════════════════════════════════════════════════════

if not st.session_state["logged_in"]:
    login_page()
else:
    role = st.session_state.get("role", "")
    if role == "Admin":
        admin_dashboard()
    elif role == "Hospital":
        hospital_dashboard()
    elif role == "Patient":
        patient_dashboard()
    else:
        st.error("Unknown authorization role. Please sign out and sign in again.")
        if st.button("Sign Out", key="unknown_role_logout"):
            auth.logout()
            st.rerun()
