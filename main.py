import requests
from bs4 import BeautifulSoup
import yfinance as yf
import smtplib
import schedule
import time
from email.mime.text import MIMEText
import os

# Fetch Stock News
def get_news_stocks(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('a', class_='Card-title')
        return [(headline.get_text(), headline.get('href', url)) for headline in headlines[:10]]  # Limit to 10 headlines
    except Exception as e:
        print(f"Error fetching stock news: {e}")
        return []

# Fetch Crypto News
def get_news_crypto(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all(['h6', 'h3'])
        return [(headline.get_text(), headline.find('a')['href']) for headline in headlines if headline.find('a')][:10]
    except Exception as e:
        print(f"Error fetching crypto news: {e}")
        return []

# Fetch Stock Price
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    try:
        return stock.info.get('regularMarketPrice', "Price not available")
    except Exception as e:
        print(f"Error retrieving stock price for {ticker}: {e}")
        return "Price not available"

# Fetch Crypto Price
def get_crypto_price(coin_id):
    try:
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
        response = requests.get(url, timeout=10).json()
        return response[coin_id]['usd']
    except Exception as e:
        print(f"Error fetching crypto price: {e}")
        return "Price data not available"

# Create Email Content
def create_email_content(stock_news, crypto_news, stock_prices, crypto_prices):
    content = "Today's News and Prices\n\nStock News:\n"
    content += '\n'.join([f"{headline}: {link}" for headline, link in stock_news]) + "\n\n"
    content += "Crypto News:\n"
    content += '\n'.join([f"{headline}: {link}" for headline, link in crypto_news]) + "\n\n"
    content += "Stock Prices:\n" + '\n'.join([f"{ticker}: ${price}" for ticker, price in stock_prices.items()]) + "\n\n"
    content += "Crypto Prices:\n" + '\n'.join([f"{coin}: ${price}" for coin, price in crypto_prices.items()])
    return content

# Send Email Function
def send_email(subject, content, to_email):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            server.sendmail(os.getenv('EMAIL_USER'), to_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Job to Fetch News and Send Email
def job():
    crypto_news = get_news_crypto('https://www.coindesk.com/')
    stock_news = get_news_stocks('https://www.cnbc.com/stocks/')
    stock_prices = {'AAPL': get_stock_price('AAPL'), 'COIN': get_stock_price('COIN')}
    crypto_prices = {'bitcoin': get_crypto_price('bitcoin')}

    email_content = create_email_content(stock_news, crypto_news, stock_prices, crypto_prices)
    send_email("Daily Stock and Crypto Update", email_content, "alichukwucp@gmail.com")

# Schedule and Run
schedule.every().day.at("14:12").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)