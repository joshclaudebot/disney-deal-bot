import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.message import EmailMessage

def get_disney_deals():
    deals = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # SOURCE 1: MouseSavers (The Gold Standard for specific discounts)
    try:
        r = requests.get("https://www.mousesavers.com/current-walt-disney-world-money-saving-offers/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Grabbing the bolded "strong" tags which usually contain the deal titles
        for offer in soup.find_all('strong', limit=8):
            txt = offer.get_text(strip=True)
            if len(txt) > 20: # Filters out small UI text
                deals.append(f"💰 MouseSavers: {txt}")
    except Exception as e:
        print(f"MouseSavers Error: {e}")

    # SOURCE 2: Disney Parks Blog (The "Influencer" Source)
    try:
        # We use their 'Latest Stories' section
        r = requests.get("https://disneyparksblog.com/latest-stories/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Looking for the headlines of the newest posts
        for title in soup.find_all('h2', limit=5):
            deals.append(f"🗞️ Parks Blog: {title.get_text(strip=True)}")
    except Exception as e:
        print(f"Parks Blog Error: {e}")

    # SOURCE 3: Disney Food Blog (RSS Feed - Very reliable)
    try:
        # RSS feeds are 'cleaner' for code to read than standard websites
        r = requests.get("https://www.disneyfoodblog.com/feed/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'xml') # Note 'xml' parser here
        for item in soup.find_all('item', limit=5):
            deals.append(f"🍕 Food Blog: {item.title.get_text(strip=True)}")
    except Exception as e:
        print(f"Food Blog Error: {e}")

    return deals

def send_email(deals):
    gmail_user = "YOUR_EMAIL@gmail.com" # <--- Your Gmail
    gmail_password = os.environ.get('GMAIL_PASS') # Pulled from GitHub Secrets

    msg = EmailMessage()
    msg['Subject'] = f"✨ Disney Daily: {len(deals)} Updates Found"
    msg['From'] = gmail_user
    msg['To'] = gmail_user

    if not deals:
        body = "Bot ran successfully, but all sources returned 0 results. Check the URLs!"
    else:
        body = "Here is your morning Disney intelligence summary:\n\n" + "\n".join(deals)
    
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Email failed: {e}")

if __name__ == "__main__":
    results = get_disney_deals()
    send_email(results)
