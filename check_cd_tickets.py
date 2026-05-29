import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

EMAIL_TO = "jaroslav_burda@seznam.cz"
EMAIL_FROM = os.environ["SMTP_FROM"]
SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]

STATE_FILE = "state.txt"


def already_notified():
    return os.path.exists(STATE_FILE)


def mark_notified():
    with open(STATE_FILE, "w") as f:
        f.write("notified")


def send_email():
    msg = MIMEText("Tickets are now available for 20. 9. 2026 Praha → Mošnov,Ostrava Airport.")
    msg["Subject"] = "ČD Ticket Availability Alert"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(SMTP_SERVER) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())


def tickets_available():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.cd.cz/")

        try:
            page.get_by_role("button", name="Souhlasím").click(timeout=3000)
        except:
            pass

        page.get_by_label("Odkud").fill("Praha hl.n.")
        page.get_by_label("Kam").fill("Mošnov,Ostrava Airport")
        page.get_by_placeholder("Datum").fill("20. 9. 2026")


        page.get_by_role("button", name="Vyhledat spojení").click()

        page.wait_for_timeout(8000)

        content = page.content()
        browser.close()

        return "Koupit jízdenku" in content


def main():
    if already_notified():
        print("Already notified earlier. Exiting.")
        return

    if tickets_available():
        send_email()
        mark_notified()
        print("Tickets available — email sent.")
    else:
        print("No tickets yet.")


if __name__ == "__main__":
    main()
