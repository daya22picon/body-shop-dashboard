# ============================================================
# tabs/customers.py  —  Tab 2: Customer Database
#
# Features:
#   - Add new customers with full contact + vehicle details
#   - Saves to customers.csv automatically
#   - Searchable table across name, RO#, VIN, make/model
#   - Click any row to see full details
#   - Edit or delete any customer
# ============================================================

import streamlit as st
import pandas as pd
import os
from datetime import date

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "customers.csv")

COLUMNS = [
    "RO#", "Box#", "Customer Name", "Phone", "Email",
    "Vehicle Year", "Vehicle Make", "Vehicle Model", "Color", "VIN",
    "Payment Type", "Insurance Company", "Date Added", "Notes"
]


def load_customers():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def save_customers(df):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, index=False)


def show():
    st.header(" All County Collision Customer Database")

    # Load customers into session state on first load
    if "customers_df" not in st.session_state:
        st.session_state.customers_df = load_customers()
    if "editing_customer_idx" not in st.session_state:
        st.session_state.editing_customer_idx = None

    editing = st.session_state.editing_customer_idx is not None
    df      = st.session_state.customers_df

    # Pre-fill form if editing an existing customer
    if editing:
        c = df.loc[st.session_state.editing_customer_idx]
        st.info(f"Editing **{c['Customer Name']}** — update the fields and click Save.")
        def_ro       = c["RO#"]
        def_box      = c["Box#"]
        def_name     = c["Customer Name"]
        def_phone    = c["Phone"]
        def_email    = c["Email"]
        def_year     = c["Vehicle Year"]
        def_make     = c["Vehicle Make"]
        def_model    = c["Vehicle Model"]
        def_color    = c["Color"]
        def_vin      = c["VIN"]
        def_payment  = c["Payment Type"] if c["Payment Type"] in ["Insurance", "Cash"] else "Insurance"
        def_ins      = c["Insurance Company"]
        def_notes    = c["Notes"] if "Notes" in c else ""
    else:
        def_ro = def_box = def_name = def_phone = def_email = ""
        def_year = def_make = def_model = def_color = def_vin = def_notes =def_ins = ""
        def_payment = "Insurance"

    # ── Add / Edit Form ──────────────────────────────────────
    label = "Edit Customer" if editing else "Add New Customer"
    with st.expander(label, expanded=True):

        col1, col2, col3 = st.columns(3)
        with col1:
            ro_number = st.text_input("RO # (Job Number)", value=def_ro, placeholder="e.g. RO-1042")
        with col2:
            box_number = st.text_input("Box #", value=def_box, placeholder="e.g. B-12")
        with col3:
            payment_type = st.selectbox("Payment Type", ["Insurance", "Cash"],
                                        index=0 if def_payment == "Insurance" else 1)

        col4, col5, col6 = st.columns(3)
        with col4:
            customer_name = st.text_input("Customer Name", value=def_name)
        with col5:
            phone = st.text_input("Phone Number", value=def_phone, placeholder="e.g. 516-555-0100")
        with col6:
            email = st.text_input("Email", value=def_email, placeholder="optional")

        col7, col8, col9, col10 = st.columns(4)
        with col7:
            vehicle_year = st.text_input("Year", value=def_year, placeholder="e.g. 2019")
        with col8:
            vehicle_make = st.text_input("Make", value=def_make, placeholder="e.g. Toyota")
        with col9:
            vehicle_model = st.text_input("Model", value=def_model, placeholder="e.g. Camry")
        with col10:
            color = st.text_input("Color", value=def_color, placeholder="e.g. Silver")

        col11, col12 = st.columns(2)
        with col11:
            vin = st.text_input("VIN", value=def_vin, placeholder="17-character VIN")
        with col12:
            if payment_type == "Insurance":
                insurance_company = st.text_input("Insurance Company", value=def_ins)
            else:
                insurance_company = ""

        notes = st.text_area("Notes / Comments", value=def_notes, placeholder="Any additional info about this job or customer...", height=100)

        btn_label = "Update Customer" if editing else "Save Customer"
        if st.button(btn_label, type="primary", use_container_width=True):
            if not ro_number.strip():
                st.error("RO # is required.")
            elif not customer_name.strip():
                st.error("Customer Name is required.")
            else:
                record = {
                    "RO#":               ro_number.strip(),
                    "Box#":              box_number.strip(),
                    "Customer Name":     customer_name.strip(),
                    "Phone":             phone.strip(),
                    "Email":             email.strip(),
                    "Vehicle Year":      vehicle_year.strip(),
                    "Vehicle Make":      vehicle_make.strip(),
                    "Vehicle Model":     vehicle_model.strip(),
                    "Color":             color.strip(),
                    "VIN":               vin.strip(),
                    "Payment Type":      payment_type,
                    "Insurance Company": insurance_company.strip(),
                    "Date Added":        str(date.today()),
                    "Notes":             notes.strip()
                }

                if editing:
                    for key, val in record.items():
                        st.session_state.customers_df.at[
                            st.session_state.editing_customer_idx, key] = val
                    st.session_state.editing_customer_idx = None
                    st.success(f"Customer **{customer_name}** updated!")
                else:
                    new_row = pd.DataFrame([record])
                    st.session_state.customers_df = pd.concat(
                        [st.session_state.customers_df, new_row], ignore_index=True
                    )
                    st.success(f"Customer **{customer_name}** (RO# {ro_number}) saved!")

                save_customers(st.session_state.customers_df)
                st.rerun()

        if editing:
            if st.button("✖️ Cancel Edit", use_container_width=True):
                st.session_state.editing_customer_idx = None
                st.rerun()

    st.markdown("---")

    # ── Search & Table ───────────────────────────────────────
    st.subheader("All Customers")

    df = st.session_state.customers_df

    if df.empty:
        st.info("No customers yet. Add your first one above!")
        return

    # Summary metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Customers", len(df))
    m2.metric("Insurance Jobs",  len(df[df["Payment Type"] == "Insurance"]))
    m3.metric("Cash Jobs",       len(df[df["Payment Type"] == "Cash"]))

    st.markdown(" ")

    search = st.text_input("Search", placeholder="Name, RO#, VIN, make, model, box...")
    if search:
        mask = (
            df["Customer Name"].str.contains(search, case=False, na=False) |
            df["RO#"].str.contains(search, case=False, na=False)           |
            df["VIN"].str.contains(search, case=False, na=False)           |
            df["Vehicle Make"].str.contains(search, case=False, na=False)  |
            df["Vehicle Model"].str.contains(search, case=False, na=False) |
            df["Box#"].str.contains(search, case=False, na=False)          |
            df["Phone"].str.contains(search, case=False, na=False)
        )
        filtered = df[mask].copy()
    else:
        filtered = df.copy()
        filtered["Box# Sort"] = pd.to_numeric(filtered["Box#"], errors="coerce")
        filtered = filtered.sort_values(by="Box# Sort", ascending=True, na_position="last")
        filtered = filtered.drop(columns=["Box# Sort"])

    st.caption(f"Showing {len(filtered)} of {len(df)} customers")

    preview_cols = ["RO#", "Box#", "Customer Name", "Phone",
                    "Vehicle Year", "Vehicle Make", "Vehicle Model", "Payment Type"]

    event = st.dataframe(
        filtered[preview_cols],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # ── Selected Customer Detail ─────────────────────────────
    selected_rows = event.selection.rows
    if selected_rows:
        original_idx = filtered.iloc[selected_rows[0]].name
        customer     = df.loc[original_idx]

        st.markdown("---")
        st.subheader(f"{customer['Customer Name']}  |  RO# {customer['RO#']}")

        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**Contact Information**")
            st.write(f"Phone: {customer['Phone'] or '—'}")
            st.write(f"Email: {customer['Email'] or '—'}")
            st.write(f"Box #: {customer['Box#'] or '—'}")
            st.write(f"Date Added: {customer['Date Added'] or '—'}")
            st.write(f"Payment: {customer['Payment Type']}")
            if customer['Payment Type'] == "Insurance":
                st.write(f"Insurance: {customer['Insurance Company'] or '—'}")
        with d2:
            st.markdown("**Vehicle Information**")
            st.write(f"{customer['Vehicle Year']} {customer['Vehicle Make']} {customer['Vehicle Model']}")
            st.write(f"Color: {customer['Color'] or '—'}")
            st.write(f"VIN: {customer['VIN'] or '—'}")

        if customer.get("Notes"):
            st.markdown("**Notes**")
            st.info(customer["Notes"])

        st.markdown(" ")
        ba, bb = st.columns(2)
        with ba:
            if st.button("Edit this customer", use_container_width=True):
                st.session_state.editing_customer_idx = original_idx
                st.rerun()
        with bb:
            if st.button("Delete this customer", type="secondary", use_container_width=True):
                st.session_state.customers_df = df.drop(
                    index=original_idx).reset_index(drop=True)
                save_customers(st.session_state.customers_df)
                st.success("Customer deleted.")
                st.rerun()