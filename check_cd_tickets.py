import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

EMAIL_TO = "jaroslav_burda_test@seznam.cz"
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

        # Open CD.cz
        page.goto("https://www.cd.cz/")

        # Accept cookies if present
        try:
            page.get_by_role("button", name="Souhlasím").click(timeout=3000)
        except:
            pass

        # Fill "From" and "To"
        page.get_by_label("Odkud").fill("Praha hl.n.")
        page.get_by_label("Kam").fill("Mošnov,Ostrava Airport")

        # --- DATE PICKER FIXED SECTION ---
        # Click the date input (React datepicker)
        page.locator("input.react-datepicker-ignore-onclickoutside").click()

        # Wait for calendar
        page.wait_for_selector("div.react-datepicker")

        # Select year
        page.locator("select.react-datepicker__year-select").select_option("2026")

        # Select month (0 = Jan, 8 = Sep)
        page.locator("select.react-datepicker__month-select").select_option("8")

        # Select day 20
        page.locator("div.react-datepicker__day--020").click()
        # --- END DATE PICKER ---

        # Click search
        page.get_by_role("button", name="Vyhledat spojení").click()

        # Wait for results to load
        page.wait_for_timeout(8000)

        # Check if "Koupit jízdenku" appears
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
