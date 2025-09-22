import os
import streamlit as st
try:
    import pandas as pd  # type: ignore
except Exception:  # optional dependency
    pd = None
from salesactivator.db.store import DB
from salesactivator.emailer.sender import EmailSender
from salesactivator.utils.config import Settings

st.set_page_config(page_title="SalesActivator – MICE US", layout="wide")
settings = Settings()
db = DB(settings.DB_PATH)
sender = EmailSender(settings)

st.title("SalesActivator – MICE (US Direct Segment)")

with st.sidebar:
    st.header("Actions")
    if st.button("Init DB"):
        db.init()
        st.success("DB initialized")
    if st.button("Show Due Emails"):
        st.session_state["show_due"] = True
    if st.button("Send Due Now"):
        count = sender.send_due(db)
        st.success(f"Sent {count} emails")

# Leads overview
st.subheader("Leads Overview")
leads_df = db.df("""
SELECT leads.id, companies.name as company, contacts.full_name as contact,
       contacts.email, leads.status, leads.created_at
FROM leads
LEFT JOIN companies ON leads.company_id = companies.id
LEFT JOIN contacts ON leads.contact_id = contacts.id
ORDER BY leads.created_at DESC
LIMIT 1000
""")
st.dataframe(leads_df, use_container_width=True)

# Email queue
st.subheader("Email Queue (Next 100)")
queue_df = db.df("""
SELECT email_queue.id, email_queue.lead_id, email_queue.step, email_queue.status,
       email_queue.scheduled_at, email_queue.last_attempt_at
FROM email_queue
ORDER BY email_queue.scheduled_at ASC
LIMIT 100
""")
st.dataframe(queue_df, use_container_width=True)

# Companies
with st.expander("Companies (first 200)"):
    companies_df = db.df("SELECT id, name, website, city, state, country, source, created_at FROM companies ORDER BY created_at DESC LIMIT 200")
    st.dataframe(companies_df, use_container_width=True)

# Contacts
with st.expander("Contacts (first 200)"):
    contacts_df = db.df("SELECT id, company_id, full_name, role, email, phone FROM contacts ORDER BY id DESC LIMIT 200")
    st.dataframe(contacts_df, use_container_width=True)

st.caption("All components run locally and use only free libraries and public web data. Use responsibly.")
