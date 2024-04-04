import requests
from datetime import date, timedelta
import smtplib


def stock_market():
    # Stock API config
    STOCK_NAME = "the code of your stock of choice"
    COMPANY_NAME = "the name of the company, used for scanning the news"

    STOCK_ENDPOINT = "https://www.alphavantage.co/query"
    STOCK_API_KEY = "your api key"
    FUNCTION = "TIME_SERIES_DAILY"
    STOCK_PARAMETERS = {
        "function": FUNCTION,
        "symbol": STOCK_NAME,
        "apikey": STOCK_API_KEY
    }

    # Define yesterday for grabbing news articles
    today = date.today()
    yesterday = today - timedelta(days=1)

    # News API config
    NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
    NEWS_API_KEY = "your api key"
    NEWS_PARAMETERS = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME,
        "language": "en",
        "from": yesterday
    }

    # Grab all stock data for selected stock
    response_stock = requests.get(url=STOCK_ENDPOINT, params=STOCK_PARAMETERS)
    response_stock.raise_for_status()
    stock_data = response_stock.json()["Time Series (Daily)"]

    # Grab yesterday's closing stock data
    data_list = [value for (key, value) in stock_data.items()]
    yesterday_data = data_list[0]
    yesterday_closing_price = float(yesterday_data["4. close"])

    # Grab day before yesterday's closing stock data
    day_before_data = data_list[1]
    day_before_closing_price = float(day_before_data["4. close"])

    # Price change calculation
    price_change = round((1 - day_before_closing_price / yesterday_closing_price) * 100, 3)
    # price_change = 6  # Debug code

    # If the change is over 5% both positive or negative, grab yesterday's news articles
    if price_change > 5 or price_change < -5:
        response_news = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMETERS)
        response_news.raise_for_status()
        news_data = response_news.json()["articles"][:3:]
        news_list = [f"Headline: {article['title']}. \nBrief: {article['description']}\n\n" for article in
                     news_data]
        formatted_articles = "".join(news_list)

        # Send email
        my_email = "your email"
        my_password = "your password"

        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_password)
            connection.sendmail(
                from_addr=my_email,
                to_addrs=my_email,
                msg=f"Subject:{STOCK_NAME}: {price_change}%\n\n"
                    f"{formatted_articles}".encode("utf-8")

            )

