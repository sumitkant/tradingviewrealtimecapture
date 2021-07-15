import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go


@st.cache
def nltk_downloader():
    nltk.download([
        "stopwords",
        "vader_lexicon",
    ])

@st.cache
def get_article_sentiment(mc, company, news_traceback, model):
    sc_id = mc.loc[mc.name == company, "scid"].values[0]
    if news_traceback == 'Last 30 days':
        urls = [
            f'https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={sc_id}&durationType=M&duration=1']
    elif news_traceback == 'Last 6 Months':
        urls = [
            f'https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={sc_id}&durationType=M&duration=6']
    elif news_traceback in ['2021', '2020', '2019', '2018', '2017', '2015', '2014']:
        urls = []
        for i in range(1, 4):
            u = f'https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={sc_id}&scat=&pageno={i}&next=0&durationType=Y&Year={news_traceback}&duration=1&news_type='
            urls.append(u)
    else:
        urls = []

    news_metadata = pd.DataFrame()
    news_scores = pd.DataFrame()
    for u, url in enumerate(urls):
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            articles = soup.find_all("a", {"class": "g_14bl"}, href=True)

            article_urls = ['https://www.moneycontrol.com/'+a['href'] for a in articles]
            article_titles = [a.get_text().strip() for a in articles]

            for i in range(len(article_urls)):
                article_soup = BeautifulSoup(requests.get(article_urls[i]).content, 'html.parser')
                article_schedule = article_soup.find('div', {'class':'article_schedule'}).text.strip()
                article_datetime = datetime.strptime(article_schedule[:-4], '%B %d, %Y / %I:%M %p')
                article_content = [a.text for a in article_soup.find('div', {'class': 'content_wrapper'}).find_all('p')]

                for a in article_content:
                    x = pd.DataFrame(model.polarity_scores(a), index=range(1))
                    x['article_text'] = a
                    x['news_id'] = 'P' + str(u) + sc_id + str(i)
                    x = x[sorted(x.columns)]
                    news_scores = news_scores.append(x, ignore_index=True)

                news_metadata = news_metadata.append(pd.DataFrame({
                    'news_id': ['P' + str(u) + sc_id + str(i)],
                    'title': [article_titles[i]],
                    'datetime': [article_datetime.strftime('%Y-%m-%d %H:%M')],
                }), ignore_index=True)
        except:
            pass

    mean_scores = news_scores.groupby('news_id').mean().reset_index()
    news_metadata = news_metadata.merge(mean_scores, on='news_id', how='inner')
    return news_metadata, news_scores

def app():

    st.title('News Scrape')
    st.header('Money Control')
    nltk_downloader()
    model = SentimentIntensityAnalyzer()

    mc = pd.read_csv('assets/mc_metadata.csv').drop('Unnamed: 0', axis=1)
    company = st.selectbox('Company', mc['name'].values)
    news_traceback = st.selectbox('Time', ['Last 30 days','Last 6 Months', '2021', '2020', '2019', '2018', '2017', '2015', '2014'], 2)

    nm, ns = get_article_sentiment(mc, company, news_traceback, model)

    st.header(f'Overall Sentiment in {news_traceback}')
    st.write('Share of Overall sentiment considering only positive and negative sentiments')
    overall_scores = nm[['neg', 'pos']].mean().reset_index()
    overall_scores.columns = ['sentiment', 'score']
    fig = go.Figure(data=[go.Pie(labels=overall_scores.sentiment.values, values=overall_scores.score.values,
                                 hole=.3,
                                 marker_colors=['#B53471', '#1289A7']
                                 )])
    # fig = px.pie(overall_scores, values='score', names='sentiment')
    fig.update_layout(showlegend=False)
    fig.update_traces(textinfo='percent+label')
    st.plotly_chart(fig)

    st.header('Sentiment Score for each article')
    st.table(nm)
    st.header('Sentiment for each news sentence')
    st.table(ns)

