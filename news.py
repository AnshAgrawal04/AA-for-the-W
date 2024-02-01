from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key="b313703b75dd480a99c27be963bb29cf")
# newsapi = NewsApiClient(api_key="b5863f3db9b54e89b94560e583919438") #Alternate key

top_headlines_nse = newsapi.get_top_headlines(
    q="stock market", category="business", language="en", country="in"
)["articles"][:5]

top_headlines_nse.extend(newsapi.get_top_headlines(
    q="trading", category="business", language="en", country="in"
)["articles"][:5])

top_headlines_nse.extend(newsapi.get_top_headlines(
    q="NSE", category="business", language="en", country="in"
)["articles"][:5])

top_headlines = list({article["title"]: article for article in top_headlines_nse}.values())

def get_news():
    return top_headlines