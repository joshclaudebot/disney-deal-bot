import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

# 1. SCRAPE THE DEALS
def get_disney_deals():
    url = "https://disneyworld.disney.go.com/special-offers/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    deals = []
    # This looks for the offer titles on the Disney page
    for offer in soup.find_all('h2', limit=10): 
        deals.append(offer.get_text(strip=True))
    return deals

# 2. SEND THE EMAIL
def send_email(deals):
    msg = EmailMessage()
    msg['Subject'] = "Daily Disney Deals Top 10"
    msg['From'] = "YOUR_EMAIL@gmail.com"
    msg['To'] = "YOUR_EMAIL@gmail.com"
    
    content = "Here are today's top Disney deals:\n\n" + "\n".join([f"- {d}" for d in deals])
    msg.set_content(content)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("YOUR_EMAIL@gmail.com", "YOUR_APP_PASSWORD")
        smtp.send_message(msg)

if __name__ == "__main__":
    found_deals = get_disney_deals()
    if found_deals:
        send_email(found_deals)