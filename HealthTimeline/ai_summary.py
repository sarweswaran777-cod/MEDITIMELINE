"""
MediTimeline - Clinical Medical History Summary & Intelligence Synthesis Module
Provides period-based medical history filtering and clinical intelligence summaries.
"""

import pandas as pd
from datetime import datetime, timedelta


def get_date_range(period):
    """
    Calculate start_date and end_date based on the selected period string.
    
    Supported periods:
    - "All Time"
    - "Last 7 Days"
    - "Last 30 Days"
    - "Last 2 Months"
    - "Last 3 Months"
    - "Last 6 Months"
    - "Last 1 Year"
    - "Custom Date Range"
    
    Returns:
        tuple: (start_date, end_date) as pandas Timestamps or (None, None)
    """
    end_date = pd.Timestamp.now().floor('s')

    if period == "All Time":
        return None, None
    elif period == "Last 7 Days":
        start_date = end_date - pd.Timedelta(days=7)
    elif period == "Last 30 Days":
        start_date = end_date - pd.Timedelta(days=30)
    elif period == "Last 2 Months":
        start_date = end_date - pd.DateOffset(months=2)
    elif period == "Last 3 Months":
        start_date = end_date - pd.DateOffset(months=3)
    elif period == "Last 6 Months":
        start_date = end_date - pd.DateOffset(months=6)
    elif period == "Last 1 Year":
        start_date = end_date - pd.DateOffset(years=1)
    elif period == "Custom Date Range":
        start_date = None
        end_date = None
    else:
        start_date = end_date - pd.Timedelta(days=30)

    return start_date, end_date


def generate_period_summary(hist_df, start_date=None, end_date=None):
    """
    Generates a structured clinical intelligence summary based on filtered medical history.
    Strictly separates verified record entities from analytical decision-support synthesis.
    
    Args:
        hist_df (pd.DataFrame): Medical history records dataframe.
        start_date (datetime/Timestamp/str/None): Start date for filtering records.
        end_date (datetime/Timestamp/str/None): End date for filtering records.
        
    Returns:
        str: Formatted clinical summary report with HTML & Markdown.
    """
    if hist_df is None or hist_df.empty:
        return (
            '<div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; '
            'padding:20px; text-align:center; color:#475569;">'
            '<h4 style="color:#0f2942; margin-top:0;">No Medical Records Available</h4>'
            '<p style="margin-bottom:0;">There are currently no recorded clinical events for this patient chart.</p>'
            '</div>'
        )

    # Copy dataframe to prevent mutating original data
    df = hist_df.copy()

    # Convert event_date to datetime for accurate filtering
    if 'event_date' in df.columns:
        df['parsed_date'] = pd.to_datetime(df['event_date'], errors='coerce')

        # Apply start_date filter if provided
        if start_date is not None and pd.notna(start_date):
            start_ts = pd.to_datetime(start_date).normalize()
            df = df[df['parsed_date'] >= start_ts]

        # Apply end_date filter if provided
        if end_date is not None and pd.notna(end_date):
            end_ts = pd.to_datetime(end_date).normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
            df = df[df['parsed_date'] <= end_ts]

    if df.empty:
        range_label = ""
        if start_date and end_date:
            range_label = f" ({str(start_date)[:10]} to {str(end_date)[:10]})"
        return (
            f'<div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; '
            f'padding:20px; text-align:center; color:#475569;">'
            f'<h4 style="color:#0f2942; margin-top:0;">No Records in Selected Timeframe{range_label}</h4>'
            f'<p style="margin-bottom:0;">No clinical events were logged during this specific date window. '
            f'Expand the date range filter or select <em>All Time</em> to review patient history.</p>'
            f'</div>'
        )

    # Sort records chronologically
    if 'parsed_date' in df.columns:
        df = df.sort_values(by='parsed_date', ascending=True)

    total_records = len(df)

    # Extract unique medical entities safely without hallucinating
    diagnoses = [str(d).strip() for d in df.get('diagnosis', pd.Series()).dropna().unique()
                 if str(d).strip() and str(d).strip().lower() not in ('none', 'nan', '', 'n/a')]
    surgeries = [str(s).strip() for s in df.get('surgery', pd.Series()).dropna().unique()
                 if str(s).strip() and str(s).strip().lower() not in ('none', 'nan', '', 'n/a')]
    medicines = [str(m).strip() for m in df.get('medicine', pd.Series()).dropna().unique()
                 if str(m).strip() and str(m).strip().lower() not in ('none', 'nan', '', 'n/a')]
    test_results = [str(t).strip() for t in df.get('test_result', pd.Series()).dropna().unique()
                    if str(t).strip() and str(t).strip().lower() not in ('none', 'nan', '', 'n/a')]
    hospitals = [str(h).strip() for h in df.get('hospital_name', pd.Series()).dropna().unique()
                 if str(h).strip() and str(h).strip().lower() not in ('none', 'nan', '', 'n/a')]
    doctors = [str(d).strip() for d in df.get('doctor_name', pd.Series()).dropna().unique()
               if str(d).strip() and str(d).strip().lower() not in ('none', 'nan', '', 'n/a')]

    # Date range formatting
    min_date = str(df['event_date'].min())[:10] if 'event_date' in df.columns else "N/A"
    max_date = str(df['event_date'].max())[:10] if 'event_date' in df.columns else "N/A"
    date_str = f"{min_date} to {max_date}" if min_date != max_date else f"{min_date}"

    # Build Structured Clinical Report
    lines = []
    
    # Header Card with Date Range & Scope
    lines.append(f"""
<div style="background: linear-gradient(135deg, #0f2942 0%, #163e63 100%); color: white; padding: 22px 26px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(15, 41, 66, 0.1);">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 600;">Clinical Intelligence Synthesis</div>
            <h2 style="color: white; margin: 4px 0 0 0; font-size: 1.5rem; font-weight: 700;">Patient Medical History Summary</h2>
        </div>
        <div style="background: rgba(255, 255, 255, 0.12); padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); text-align: right;">
            <div style="font-size: 0.75rem; color: #cbd5e1; text-transform: uppercase;">Analysis Period</div>
            <div style="font-size: 0.95rem; font-weight: 600; color: #ffffff;">{date_str}</div>
        </div>
    </div>
    <div style="display: flex; gap: 24px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.15); flex-wrap: wrap;">
        <div><span style="color: #94a3b8; font-size: 0.8rem;">Clinical Events:</span> <strong style="color: #38bdf8; font-size: 0.95rem;">{total_records}</strong></div>
        <div><span style="color: #94a3b8; font-size: 0.8rem;">Facilities Involved:</span> <strong style="color: #ffffff; font-size: 0.95rem;">{len(hospitals)}</strong></div>
        <div><span style="color: #94a3b8; font-size: 0.8rem;">Attending Physicians:</span> <strong style="color: #ffffff; font-size: 0.95rem;">{len(doctors)}</strong></div>
    </div>
</div>
""")

    # SECTION 1: EXTRACTED CLINICAL RECORDS (Source Data)
    lines.append("""
<div style="margin: 20px 0 10px 0; display: flex; align-items: center; gap: 8px;">
    <span style="display: inline-block; width: 4px; height: 18px; background: #0d9488; border-radius: 2px;"></span>
    <h3 style="color: #0f2942; margin: 0; font-size: 1.2rem; font-weight: 600;">Section 1: Verified Clinical Records Data</h3>
</div>
<p style="color: #64748b; font-size: 0.85rem; margin-top: 2px; margin-bottom: 16px;">
    Information directly extracted from verified electronic health entries recorded during patient consultations and hospital admissions.
</p>
""")

    # Grid of Entity Cards
    diag_items = "".join([f'<li style="margin-bottom: 4px;"><strong>{d}</strong></li>' for d in diagnoses]) if diagnoses else '<li style="color: #94a3b8;">None recorded in this period</li>'
    med_items = "".join([f'<li style="margin-bottom: 4px;"><strong>{m}</strong></li>' for m in medicines]) if medicines else '<li style="color: #94a3b8;">None recorded in this period</li>'
    surg_items = "".join([f'<li style="margin-bottom: 4px;"><strong>{s}</strong></li>' for s in surgeries]) if surgeries else '<li style="color: #94a3b8;">No surgical procedures recorded</li>'
    test_items = "".join([f'<li style="margin-bottom: 4px;">{t}</li>' for t in test_results]) if test_results else '<li style="color: #94a3b8;">No diagnostic tests recorded</li>'

    lines.append(f"""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 22px;">
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #0d9488; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <h4 style="color: #0f2942; margin: 0 0 10px 0; font-size: 0.95rem; font-weight: 600;">Recorded Diagnoses & Conditions</h4>
        <ul style="margin: 0; padding-left: 18px; font-size: 0.88rem; color: #1e293b;">
            {diag_items}
        </ul>
    </div>
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #0284c7; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <h4 style="color: #0f2942; margin: 0 0 10px 0; font-size: 0.95rem; font-weight: 600;">Prescribed Medications</h4>
        <ul style="margin: 0; padding-left: 18px; font-size: 0.88rem; color: #1e293b;">
            {med_items}
        </ul>
    </div>
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #6366f1; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <h4 style="color: #0f2942; margin: 0 0 10px 0; font-size: 0.95rem; font-weight: 600;">Surgeries & Procedures</h4>
        <ul style="margin: 0; padding-left: 18px; font-size: 0.88rem; color: #1e293b;">
            {surg_items}
        </ul>
    </div>
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #14b8a6; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <h4 style="color: #0f2942; margin: 0 0 10px 0; font-size: 0.95rem; font-weight: 600;">Laboratory & Diagnostic Tests</h4>
        <ul style="margin: 0; padding-left: 18px; font-size: 0.88rem; color: #1e293b;">
            {test_items}
        </ul>
    </div>
</div>
""")

    # Chronological Event Log
    lines.append("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
    <h4 style="color: #0f2942; margin: 0 0 14px 0; font-size: 1rem; font-weight: 600;">Chronological Clinical Event Log</h4>
""")

    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        edate = row.get('event_date', 'N/A')
        etype = row.get('event_type', 'Clinical Event')
        hname = row.get('hospital_name', '')
        doc = row.get('doctor_name', '')
        desc = row.get('description', '')
        diag = row.get('diagnosis', '')
        med = row.get('medicine', '')
        test = row.get('test_result', '')
        surg = row.get('surgery', '')
        notes = row.get('notes', '')

        meta_parts = []
        if hname:
            meta_parts.append(f"Facility: <strong>{hname}</strong>")
        if doc:
            meta_parts.append(f"Physician: <strong>{doc}</strong>")
        meta_str = " | ".join(meta_parts)

        details_html = []
        if desc:
            details_html.append(f"<div><span style='color:#64748b;'>Clinical Description:</span> {desc}</div>")
        if diag:
            details_html.append(f"<div><span style='color:#64748b;'>Diagnosis:</span> <strong style='color:#0f2942;'>{diag}</strong></div>")
        if med:
            details_html.append(f"<div><span style='color:#64748b;'>Pharmacotherapy:</span> <strong style='color:#0284c7;'>{med}</strong></div>")
        if test:
            details_html.append(f"<div><span style='color:#64748b;'>Findings / Labs:</span> {test}</div>")
        if surg:
            details_html.append(f"<div><span style='color:#64748b;'>Procedure:</span> <strong style='color:#6366f1;'>{surg}</strong></div>")
        if notes:
            details_html.append(f"<div><span style='color:#64748b;'>Clinical Notes:</span> <em>{notes}</em></div>")

        details_joined = "".join([f"<div style='margin-top: 3px; font-size: 0.86rem;'>{d}</div>" for d in details_html])

        lines.append(f"""
    <div style="border-left: 3px solid #0d9488; padding: 10px 14px; margin-bottom: 12px; background: #f8fafc; border-radius: 0 8px 8px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <strong style="color: #0f2942; font-size: 0.92rem;">{edate}</strong>
                <span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: 600; margin-left: 8px;">{etype}</span>
            </div>
            <div style="font-size: 0.8rem; color: #475569;">{meta_str}</div>
        </div>
        <div style="margin-top: 6px;">
            {details_joined}
        </div>
    </div>
""")

    lines.append("</div>")

    # SECTION 2: CLINICAL DECISION SUPPORT & HEALTH INTELLIGENCE (Derived Synthesis)
    lines.append("""
<div style="margin: 24px 0 10px 0; display: flex; align-items: center; gap: 8px;">
    <span style="display: inline-block; width: 4px; height: 18px; background: #0284c7; border-radius: 2px;"></span>
    <h3 style="color: #0f2942; margin: 0; font-size: 1.2rem; font-weight: 600;">Section 2: Clinical Decision Support & Care Continuity Insights</h3>
</div>
<p style="color: #64748b; font-size: 0.85rem; margin-top: 2px; margin-bottom: 16px;">
    Algorithmic synthesis derived from historical encounters above to support longitudinal care continuity and clinical awareness.
</p>
""")

    # Rule-based clinical insights derived strictly from records
    insights = []
    if surgeries:
        insights.append({
            "title": "Post-Surgical Follow-Up & Recovery Monitoring",
            "desc": f"Patient chart contains surgical procedures ({', '.join(surgeries)}). Verify long-term recovery markers, incision site integrity, and schedule routine post-operative evaluations."
        })
    if any("diabet" in d.lower() for d in diagnoses) or any("metformin" in m.lower() for m in medicines):
        insights.append({
            "title": "Endocrine & Glycemic Control Monitoring",
            "desc": "Active clinical markers for Type 2 Diabetes / Glycemic management noted. Continuous HbA1c and fasting blood sugar monitoring is recommended alongside dietary and pharmacological adherence."
        })
    if any("fever" in d.lower() for d in diagnoses) or any("infection" in d.lower() for d in diagnoses):
        insights.append({
            "title": "Infection Resolution & Antibiotic Stewardship",
            "desc": "Documented acute febrile or infectious episodes. Ensure complete antimicrobial regimens were fulfilled to prevent recurrence or resistance."
        })
    if medicines:
        insights.append({
            "title": "Pharmacotherapy Reconciliation",
            "desc": f"Active or recent medications recorded ({', '.join(medicines)}). Conduct regular multi-drug interaction reviews when prescribing complementary treatments."
        })

    if not insights:
        insights.append({
            "title": "Preventive Health & Longitudinal Stability",
            "desc": "No acute clinical contraindications identified in the selected historical interval. Standard routine health examinations and periodic clinical surveillance are advised."
        })

    lines.append("""
<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 18px; margin-bottom: 22px;">
""")
    for ins in insights:
        lines.append(f"""
    <div style="margin-bottom: 12px;">
        <div style="color: #166534; font-weight: 600; font-size: 0.92rem;">• {ins['title']}</div>
        <div style="color: #1e293b; font-size: 0.86rem; margin-top: 2px; padding-left: 14px;">{ins['desc']}</div>
    </div>
""")
    lines.append("</div>")

    # Safety Notice & Governance Disclaimer
    lines.append("""
<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; font-size: 0.8rem; color: #64748b; line-height: 1.4;">
    <strong>Clinical Decision Support Notice:</strong> This summary aggregates data from recorded electronic health records to support clinical decision-making. Information is structured for physician reference and must be verified by attending medical practitioners during clinical assessment.
</div>
""")

    return "\n".join(lines)
