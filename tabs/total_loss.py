# ============================================================
# tabs/total_loss.py  —  Tab 3: Storage & Fees Calculator
#
# Features:
#   - Editable fee settings saved to JSON
#   - Save jobs to a log organized by year
#   - Edit any saved job (updates in place)
#   - Print preview with full invoice layout
#   - Signature and date line on invoice
# ============================================================

import streamlit as st
from datetime import date
import pandas as pd
import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "settings.json")
LOG_FILE      = os.path.join(os.path.dirname(__file__), "..", "data", "job_log.csv")

DEFAULT_SETTINGS = {
    "storage_rate": 95.00,
    "yard_fee":     150.00,
    "admin_fee":    350.00,
    "tow_out":      175.00,
    "tow_in":       175.00,
    "tax_rate":     8.625
}

LOG_COLUMNS = [
    "RO#", "Insurance", "Customer Name", "Vehicle",
    "Date In", "Storage Until", "Total Days",
    "Storage Fee", "Tow In", "Yard Fee", "Admin Fee",
    "Tow Out", "Subtotal", "Tax", "Total", "Date Saved", "Year"
]


# ── Helpers ──────────────────────────────────────────────────

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            saved = json.load(f)
        for key, val in DEFAULT_SETTINGS.items():
            if key not in saved:
                saved[key] = val
        return saved
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_log():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE, dtype=str)
        for col in LOG_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[LOG_COLUMNS]
    return pd.DataFrame(columns=LOG_COLUMNS)


def save_log(df):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    df.to_csv(LOG_FILE, index=False)


def build_invoice_html(job, s):
    """
    Builds a full HTML invoice page for print preview.
    Opens in a new browser tab — user clicks Print from there.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Invoice - {job.get('RO#', '')}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 13px;
                color: #000;
                padding: 40px;
                max-width: 750px;
                margin: 0 auto;
            }}

            /* ── Header ── */
            .header {{
                text-align: center;
                border-bottom: 3px solid #000;
                padding-bottom: 16px;
                margin-bottom: 20px;
            }}
            .shop-name {{
                font-size: 26px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            .shop-details {{
                font-size: 12px;
                color: #333;
                margin-top: 4px;
                line-height: 1.6;
            }}
            .tax-info {{
                font-size: 11px;
                color: #555;
                margin-top: 6px;
            }}

            /* ── Invoice title ── */
            .invoice-title {{
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                margin: 16px 0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}

            /* ── Info grid ── */
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-bottom: 20px;
            }}
            .info-box {{
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 10px 14px;
            }}
            .info-box h3 {{
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #666;
                margin-bottom: 8px;
                border-bottom: 1px solid #eee;
                padding-bottom: 4px;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
                font-size: 12px;
            }}
            .info-label {{ color: #555; }}
            .info-value {{ font-weight: bold; }}

            /* ── Fee table ── */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th {{
                background: #1a1a2e;
                color: #fff;
                padding: 8px 12px;
                text-align: left;
                font-size: 12px;
            }}
            td {{
                padding: 7px 12px;
                border-bottom: 1px solid #eee;
                font-size: 12px;
            }}
            tr:nth-child(even) td {{ background: #f9f9f9; }}
            .total-row td {{
                background: #1a1a2e !important;
                color: #fff;
                font-weight: bold;
                font-size: 14px;
                border-top: 2px solid #000;
            }}
            .subtotal-row td {{
                background: #f0f0f0 !important;
                font-weight: bold;
            }}
            .amount {{ text-align: right; }}

            /* ── Signature ── */
            .signature-section {{
                margin-top: 40px;
                border-top: 1px solid #ccc;
                padding-top: 20px;
            }}
            .sig-title {{
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #666;
                margin-bottom: 30px;
            }}
            .sig-grid {{
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 40px;
                margin-top: 10px;
            }}
            .sig-line {{
                border-bottom: 1px solid #000;
                padding-bottom: 4px;
                margin-bottom: 4px;
            }}
            .sig-label {{
                font-size: 10px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            /* ── Footer ── */
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 10px;
                color: #888;
                border-top: 1px solid #eee;
                padding-top: 10px;
            }}

            /* ── Print button (hidden when printing) ── */
            .print-btn {{
                display: block;
                margin: 0 auto 30px;
                padding: 10px 32px;
                background: #1a1a2e;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                cursor: pointer;
                letter-spacing: 1px;
            }}
            @media print {{
                .print-btn {{ display: none; }}
                body {{ padding: 20px; }}
            }}
        </style>
    </head>
    <body>

        <button class="print-btn" onclick="window.print()">🖨️ Print Invoice</button>

        <!-- Shop Header -->
        <div class="header">
            <div class="shop-name">All County Collision</div>
            <div class="shop-details">
                1289 Hempstead Turnpike · Elmont, NY 11003<br>
                (516) 502-2712
            </div>
            <div class="tax-info">
                TAX ID #262881962 &nbsp;|&nbsp; FACILITY #7106614
            </div>
        </div>

        <div class="invoice-title">Storage Invoice</div>

        <!-- Customer & Vehicle Info -->
        <div class="info-grid">
            <div class="info-box">
                <h3>Customer Information</h3>
                <div class="info-row">
                    <span class="info-label">Name</span>
                    <span class="info-value">{job.get('Customer Name', '—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Insurance</span>
                    <span class="info-value">{job.get('Insurance', '—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">RO #</span>
                    <span class="info-value">{job.get('RO#', '—')}</span>
                </div>
            </div>
            <div class="info-box">
                <h3>Vehicle Information</h3>
                <div class="info-row">
                    <span class="info-label">Vehicle</span>
                    <span class="info-value">{job.get('Vehicle', '—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Date In</span>
                    <span class="info-value">{job.get('Date In', '—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Storage Until</span>
                    <span class="info-value">{job.get('Storage Until', '—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Total Days</span>
                    <span class="info-value">{job.get('Total Days', '—')} days</span>
                </div>
            </div>
        </div>

        <!-- Fee Breakdown Table -->
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Note</th>
                    <th class="amount">Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Storage Fee</td>
                    <td>{job.get('Total Days', '—')} days × $95/day</td>
                    <td class="amount">{job.get('Storage Fee', '—')}</td>
                </tr>
                <tr>
                    <td>Tow In Fee</td>
                    <td></td>
                    <td class="amount">{job.get('Tow In', '—')}</td>
                </tr>
                <tr>
                    <td>Yard Fee</td>
                    <td></td>
                    <td class="amount">{job.get('Yard Fee', '—')}</td>
                </tr>
                <tr>
                    <td>Admin / Labor Fee</td>
                    <td></td>
                    <td class="amount">{job.get('Admin Fee', '—')}</td>
                </tr>
                <tr>
                    <td>Tow Out Fee</td>
                    <td></td>
                    <td class="amount">{job.get('Tow Out', '—')}</td>
                </tr>
                <tr class="subtotal-row">
                    <td colspan="2">Subtotal</td>
                    <td class="amount">{job.get('Subtotal', '—')}</td>
                </tr>
                <tr>
                    <td colspan="2">Tax (8.625%)</td>
                    <td class="amount">{job.get('Tax', '—')}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="2">TOTAL DUE</td>
                    <td class="amount">{job.get('Total', '—')}</td>
                </tr>
            </tbody>
        </table>

        <!-- Signature Section -->
        <div class="signature-section">
            <div class="sig-title">Release Authorization</div>
            <div class="sig-grid">
                <div>
                    <div class="sig-line">&nbsp;</div>
                    <div class="sig-label">Customer Signature</div>
                </div>
                <div>
                    <div class="sig-line">&nbsp;</div>
                    <div class="sig-label">Date</div>
                </div>
            </div>
        </div>

        <div class="footer">
            Thank you for your business · All County Collision · (516) 502-2712
        </div>

    </body>
    </html>
    """


# ── Main Tab ─────────────────────────────────────────────────

def show():
    st.header("🧮 Storage & Fees Calculator")

    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()
    if "job_log" not in st.session_state:
        st.session_state.job_log = load_log()
    if "editing_idx" not in st.session_state:
        st.session_state.editing_idx = None  # tracks which job is being edited

    s = st.session_state.settings

    # ── Settings Panel ───────────────────────────────────────
    with st.expander("⚙️ Fee Settings — click to edit prices", expanded=False):
        st.markdown("Update any fee and click **Save Settings**. Applies to all future calculations.")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_storage_rate = st.number_input("Storage Rate ($/day)", min_value=0.00, value=float(s["storage_rate"]), step=1.00, format="%.2f")
            new_tow_in       = st.number_input("Default Tow In ($)",   min_value=0.00, value=float(s["tow_in"]),       step=5.00, format="%.2f")
        with col2:
            new_yard_fee  = st.number_input("Yard Fee ($)",          min_value=0.00, value=float(s["yard_fee"]),  step=5.00, format="%.2f")
            new_admin_fee = st.number_input("Admin / Labor Fee ($)", min_value=0.00, value=float(s["admin_fee"]), step=5.00, format="%.2f")
        with col3:
            new_tow_out  = st.number_input("Tow Out ($)",  min_value=0.00,  value=float(s["tow_out"]),  step=5.00,  format="%.2f")
            new_tax_rate = st.number_input("Tax Rate (%)", min_value=0.000, value=float(s["tax_rate"]), step=0.001, format="%.3f")

        if st.button("💾 Save Settings", type="primary"):
            st.session_state.settings = {
                "storage_rate": new_storage_rate, "yard_fee": new_yard_fee,
                "admin_fee": new_admin_fee, "tow_out": new_tow_out,
                "tow_in": new_tow_in, "tax_rate": new_tax_rate
            }
            save_settings(st.session_state.settings)
            st.success("✅ Settings saved!")
            st.rerun()

    st.markdown("---")

    # ── Determine default values for the form ────────────────
    # If editing a saved job, pre-fill the form with that job's data
    editing = st.session_state.editing_idx is not None
    log_df  = st.session_state.job_log

    if editing:
        job = log_df.loc[st.session_state.editing_idx]
        st.info(f"✏️ Editing job **RO# {job['RO#']}** — update the fields below and click Save.")
        default_ro       = job["RO#"]
        default_ins      = job["Insurance"]
        default_cust     = job["Customer Name"]
        default_vehicle  = job["Vehicle"]
        default_date_in  = date.fromisoformat(job["Date In"])
        default_date_out = date.fromisoformat(job["Storage Until"])
        # Parse tow in from saved string like "$175.00"
        try:
            default_tow_in = float(job["Tow In"].replace("$", "").replace(",", ""))
        except Exception:
            default_tow_in = float(s["tow_in"])
    else:
        default_ro       = ""
        default_ins      = ""
        default_cust     = ""
        default_vehicle  = ""
        default_date_in  = date.today()
        default_date_out = date.today()
        default_tow_in   = float(s["tow_in"])

    # ── Job Form ─────────────────────────────────────────────
    st.subheader("✏️ Edit Job" if editing else "New Job")

    col4, col5, col6 = st.columns(3)
    with col4:
        ro_number = st.text_input("RO #", value=default_ro, placeholder="e.g. RO-1042")
    with col5:
        insurance = st.text_input("Insurance Company", value=default_ins)
    with col6:
        customer_name = st.text_input("Customer Name", value=default_cust)

    year_make_model = st.text_input("Year, Make & Model", value=default_vehicle, placeholder="e.g. 2018 Honda Accord")

    st.markdown("#### Storage Period")
    col7, col8 = st.columns(2)
    with col7:
        date_in = st.date_input("Date In", value=default_date_in)
    with col8:
        storage_until = st.date_input("Storage Until", value=default_date_out)

    if storage_until >= date_in:
        total_days = (storage_until - date_in).days + 1
    else:
        total_days = 0
        st.warning("⚠️ 'Storage Until' is before 'Date In' — check the dates.")

    storage_fee = total_days * s["storage_rate"]

    col9, col10 = st.columns(2)
    col9.metric("Total Days",   f"{total_days} days")
    col10.metric("Storage Fee", f"${storage_fee:,.2f}", help=f"{total_days} days × ${s['storage_rate']}/day")

    st.markdown("#### Fees")
    col11, col12, col13, col14 = st.columns(4)
    with col11:
        tow_in = st.number_input("Tow In ($)", min_value=0.00, value=default_tow_in, step=5.00, format="%.2f")
    with col12:
        st.metric("Yard Fee",      f"${s['yard_fee']:,.2f}")
    with col13:
        st.metric("Admin / Labor", f"${s['admin_fee']:,.2f}")
    with col14:
        st.metric("Tow Out",       f"${s['tow_out']:,.2f}")

    subtotal = storage_fee + tow_in + s["yard_fee"] + s["admin_fee"] + s["tow_out"]
    tax      = subtotal * (s["tax_rate"] / 100)
    total    = subtotal + tax

    st.markdown("---")
    st.subheader("Totals")
    t1, t2, t3 = st.columns(3)
    t1.metric("Subtotal",                f"${subtotal:,.2f}")
    t2.metric(f"Tax ({s['tax_rate']}%)", f"${tax:,.2f}")
    t3.metric("💰 Total",                f"${total:,.2f}")

    st.markdown("---")
    st.subheader("Itemized Breakdown")
    breakdown = pd.DataFrame({
        "Line Item": ["Storage Fee", "Tow In", "Yard Fee", "Admin / Labor Fee", "Tow Out", "Subtotal", f"Tax ({s['tax_rate']}%)", "TOTAL"],
        "Amount":    [f"${storage_fee:,.2f}", f"${tow_in:,.2f}", f"${s['yard_fee']:,.2f}", f"${s['admin_fee']:,.2f}", f"${s['tow_out']:,.2f}", f"${subtotal:,.2f}", f"${tax:,.2f}", f"${total:,.2f}"],
        "Note":      [f"{total_days} days × ${s['storage_rate']}/day", "Per job", "Fixed", "Fixed", "Fixed", "", "", ""]
    })
    st.dataframe(breakdown, use_container_width=True, hide_index=True)

    # ── Save / Update button ─────────────────────────────────
    st.markdown("---")
    btn_label = "💾 Update Job" if editing else "💾 Save Job to Log"

    if st.button(btn_label, type="primary", use_container_width=True):
        if not ro_number.strip():
            st.error("Please enter an RO # before saving.")
        else:
            job_record = {
                "RO#": ro_number.strip(), "Insurance": insurance.strip(),
                "Customer Name": customer_name.strip(), "Vehicle": year_make_model.strip(),
                "Date In": str(date_in), "Storage Until": str(storage_until),
                "Total Days": str(total_days), "Storage Fee": f"${storage_fee:,.2f}",
                "Tow In": f"${tow_in:,.2f}", "Yard Fee": f"${s['yard_fee']:,.2f}",
                "Admin Fee": f"${s['admin_fee']:,.2f}", "Tow Out": f"${s['tow_out']:,.2f}",
                "Subtotal": f"${subtotal:,.2f}", "Tax": f"${tax:,.2f}",
                "Total": f"${total:,.2f}", "Date Saved": str(date.today()),
                "Year": str(date_in.year)   # used for grouping by year
            }

            if editing:
                # Overwrite the existing row in place
                for key, val in job_record.items():
                    st.session_state.job_log.at[st.session_state.editing_idx, key] = val
                st.session_state.editing_idx = None
                st.success(f"✅ Job RO# {ro_number} updated!")
            else:
                new_row = pd.DataFrame([job_record])
                st.session_state.job_log = pd.concat(
                    [st.session_state.job_log, new_row], ignore_index=True
                )
                st.success(f"✅ Job RO# {ro_number} saved!")

            save_log(st.session_state.job_log)
            st.rerun()

    # Cancel edit button
    if editing:
        if st.button("✖️ Cancel Edit", use_container_width=True):
            st.session_state.editing_idx = None
            st.rerun()

    # ── Job Log grouped by Year ──────────────────────────────
    st.markdown("---")
    st.subheader("📋 Saved Job Log")

    log_df = st.session_state.job_log

    if log_df.empty:
        st.info("No jobs saved yet. Fill in the form above and click 'Save Job to Log'.")
        return

    st.caption(f"{len(log_df)} total job(s) on record")

    # Get all years present in the log, most recent first
    if "Year" not in log_df.columns or log_df["Year"].isna().all():
        log_df["Year"] = log_df["Date In"].str[:4]

    years = sorted(log_df["Year"].dropna().unique().tolist(), reverse=True)

    for year in years:
        year_jobs = log_df[log_df["Year"] == year].copy()
        st.markdown(f"### 📅 {year}  —  {len(year_jobs)} job(s)")

        event = st.dataframe(
            year_jobs[["RO#", "Customer Name", "Vehicle", "Date In", "Storage Until", "Total Days", "Total"]],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"log_{year}"   # unique key per year so Streamlit doesn't confuse them
        )

        selected_rows = event.selection.rows
        if selected_rows:
            # Map back to the original index in the full dataframe
            original_idx = year_jobs.iloc[selected_rows[0]].name
            job = log_df.loc[original_idx]

            st.markdown("---")
            st.subheader(f"📄 {job['Customer Name'] or 'Job'}  |  RO# {job['RO#']}")

            d1, d2 = st.columns(2)
            with d1:
                st.write(f"**Insurance:** {job['Insurance'] or '—'}")
                st.write(f"**Vehicle:** {job['Vehicle'] or '—'}")
                st.write(f"**Date In:** {job['Date In']}")
                st.write(f"**Storage Until:** {job['Storage Until']}")
                st.write(f"**Total Days:** {job['Total Days']}")
            with d2:
                st.write(f"**Storage Fee:** {job['Storage Fee']}")
                st.write(f"**Tow In:** {job['Tow In']}")
                st.write(f"**Yard Fee:** {job['Yard Fee']}")
                st.write(f"**Admin Fee:** {job['Admin Fee']}")
                st.write(f"**Subtotal:** {job['Subtotal']}")
                st.write(f"**Tax:** {job['Tax']}")
                st.markdown(f"### Total: {job['Total']}")

            # Action buttons
            ba, bb, bc = st.columns(3)

            with ba:
                if st.button("✏️ Edit this job", key=f"edit_{original_idx}"):
                    st.session_state.editing_idx = original_idx
                    st.rerun()

            with bb:
                # Print preview — generates HTML invoice and opens in new tab
                invoice_html = build_invoice_html(job.to_dict(), s)
                # Encode as base64 data URL so it opens in the browser
                
            if st.button("🖨️ Print Preview", key=f"print_{original_idx}", use_container_width=True):
                current = st.session_state.get(f"show_preview_{original_idx}", False)
                st.session_state[f"show_preview_{original_idx}"] = not current

            if st.session_state.get(f"show_preview_{original_idx}"):
                import streamlit.components.v1 as components
                invoice_html = build_invoice_html(job.to_dict(), s)
                components.html(invoice_html, height=900, scrolling=True)

            with bc:
                if st.button("🗑️ Delete", key=f"del_{original_idx}", type="secondary"):
                    st.session_state.job_log = log_df.drop(index=original_idx).reset_index(drop=True)
                    save_log(st.session_state.job_log)
                    st.success("Job deleted.")
                    st.rerun()