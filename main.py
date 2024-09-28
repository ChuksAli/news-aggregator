import requests
from bs4 import BeautifulSoup
import yfinance as yf
import smtplib
import schedule
import time
from email.mime.text import MIMEText
import os

def job():
    # Function to get news
    def get_news_stocks(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            headlines = soup.find_all('a', class_='Card-title')
            
            news_items = []
            for headline in headlines:
                link = headline.get('href')
                text = headline.get_text()
                if not link.startswith('http'):
                    link = url + link
                news_items.append((text, link))
            
            return news_items
        except Exception as e:
            print(f"Error fetching stock news: {e}")
            return []

    def get_news_crypto(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            headlines = soup.find_all(lambda tag: (tag.name == 'h6' or tag.name == 'h3'))
        
            news_items = []
            for headline in headlines:
                a_tag = headline.find('a')
                if a_tag:
                    link = a_tag.get('href')
                    text = a_tag.get_text()
                    if not link.startswith('http'):
                        link = url + link
                    news_items.append((text, link))
            
            return news_items
        except Exception as e:
            print(f"Error fetching crypto news: {e}")
            return []

    # Get news
    crypto_news = get_news_crypto('https://www.coindesk.com/')
    stock_news = get_news_stocks('https://www.cnbc.com/stocks/')

    # Function to get stock price
    def get_stock_price(ticker):
        stock = yf.Ticker(ticker)
        try:
            if 'regularMarketPrice' in stock.info:
                return stock.info['regularMarketPrice']
            else:
                return "Price data not available"
        except KeyError:
            return "Error retrieving price"
        except Exception as e:
            return f"An error occurred: {e}"

    # Stock prices dictionary
    stock_prices = {
        'AAPL': get_stock_price('AAPL'),
        'COIN': get_stock_price('COIN'),
    }

    # Function to get crypto price
    def get_crypto_price(coin_id):
        try:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
            response = requests.get(url).json()
            return response[coin_id]['usd']
        except Exception as e:
            print(f"Error fetching crypto price: {e}")
            return "Price data not available"

    # Crypto prices dictionary
    crypto_prices = {
        'bitcoin': get_crypto_price('bitcoin'),
    }

    # Function to create email content
    def create_email_content(stock_news, crypto_news, stock_prices, crypto_prices):
        content = "Today's News and Prices\n\n"
        
        content += "Stock News:\n"
        for headline, link in stock_news:
            content += f"{headline}: {link}\n"
        content += "\n"
        
        content += "Crypto News:\n"
        for headline, link in crypto_news:
            content += f"{headline}: {link}\n"
        content += "\n"
        
        content += "Stock Prices:\n"
        content += '\n'.join([f"{ticker}: ${price}" for ticker, price in stock_prices.items()]) + "\n\n"
        
        content += "Crypto Prices:\n"
        content += '\n'.join([f"{coin}: ${price}" for coin, price in crypto_prices.items()])
        
        return content

    # Generate the email content
    email_content = create_email_content(stock_news, crypto_news, stock_prices, crypto_prices)

    # Function to send the email
    def send_email(subject, content, to_email):
    # Encode email content in UTF-8
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = to_email

    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.sendmail(email_user, to_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

    # Send the email
    send_email("Daily Stock and Crypto Update", email_content, "your_email@gmail.com")

# Schedule the job to run daily at 9:30 AM
schedule.every().day.at("09:45").do(job)

# Keep the script running to check the schedule
while True:
    schedule.run_pending()
    time.sleep(1)