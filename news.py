from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key="b313703b75dd480a99c27be963bb29cf")

top_headlines_nse = newsapi.get_top_headlines(
    q="stock market", category="business", language="en", country="in"
)

def get_news():
    return top_headlines_nse