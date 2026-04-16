import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import email.utils

def is_recent(date_str):
    """Checks if a date string is within the last 5 days."""
    try:
        # Parses standard RSS date format: 'Fri, 10 Apr 2026 12:00:00 GMT'
        pub_date = email.utils.parsedate_to_datetime(date_str)
        # Remove timezone info to compare with 'now'
        pub_date = pub_date.replace(tzinfo=None)
        cutoff = datetime.now() - timedelta(days=5)
        return pub_date > cutoff
    except:
        return True # If we can't parse the date, keep the deal just in case

def get_disney_deals():
    deals = []
    headers = {"User-Agent": "Mozilla/5.0"}

    # SOURCE 1: Disney Food Blog (RSS) - Great for date filtering
    try:
        r = requests.get("https://www.disneyfoodblog.com/feed/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'xml')
        for item in soup.find_all('item', limit=10):
            title = item.title.text
            date_raw = item.pubDate.text
            if is_recent(date_raw):
                deals.append(f"🍕 Food Blog (Recent): {title}")
    except Exception as e:
        print(f"Error scraping Food Blog: {e}")

    # SOURCE 2: MouseSavers - Always included as a backup
    try:
        r = requests.get("https://www.mousesavers.com/current-walt-disney-world-money-saving-offers/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for offer in soup.find_all('strong', limit=5):
            txt = offer.get_text(strip=True)
            if len(txt) > 20:
                deals.append(f"💰 MouseSavers: {txt}")
    except Exception as e:
        print(f"Error scraping MouseSavers: {e}")

    return deals

def send_email(deals):
    gmail_user = "YOUR_EMAIL@gmail.com" # <--- Change to your email
    gmail_password = os.environ.get('GMAIL_PASS')

    msg = EmailMessage()
    msg['From'] = gmail_user
    msg['To'] = gmail_user

    if not deals:
        msg['Subject'] = "📍 Disney Bot: No New Deals Today"
        body = "The bot checked all sources but found no new deals posted within the last 5 days."
    else:
        msg['Subject'] = f"✨ Disney Daily: {len(deals)} Updates Found"
        body = "Here is your morning Disney intelligence summary:\n\n" + "\n".join(deals)
    
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Email login failed: {e}")

if __name__ == "__main__":
    results = get_disney_deals()
    send_email(results)
