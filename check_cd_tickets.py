import requests
import smtplib
from email.mime.text import MIMEText
import json
import os

API_BASE = "https://api.cd.cz/routeplanner"

ORIGIN = "5400001"   # Praha hl.n.
DEST = "3450059"     # Mošnov, Ostrava Airport
DATE = "2026-09-20"

EMAIL_TO = "jaroslav_burda_test@seznam.cz"
EMAIL_FROM = os.environ["SMTP_FROM"]
SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]

STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"notified": False}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def search_connections():
    payload = {
        "from": ORIGIN,
        "to": DEST,
        "date": DATE,
        "time": "00:00",
        "direct": False
    }
    r = requests.post(f"{API_BASE}/connections/search", json=payload)
    r.raise_for_status()
    return r.json()


def check_ticket_offer(connection):
    offer_payload = {"connection": connection}
    r = requests.post(f"{API_BASE}/tickets", json=offer_payload)
    return r.status_code == 200


def send_email():
    msg = MIMEText(f"Tickets are now available for {DATE} Praha → Mošnov Airport.")
    msg["Subject"] = "ČD Ticket Availability Alert"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(SMTP_SERVER) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())


def main():
    state = load_state()

    if state.get("notified"):
        print("Already notified earlier. Exiting.")
        return

    data = search_connections()

    for conn in data.get("connections", []):
        if check_ticket_offer(conn):
            send_email()
            state["notified"] = True
            save_state(state)
            print("Tickets available — email sent.")
            return

    print("No tickets yet.")


if __name__ == "__main__":
    main()
