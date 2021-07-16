import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import plotly.graph_objects as go


@st.cache
def nltk_downloader():
    nltk.download([
        "stopwords",
        "vader_lexicon",
    ])


@st.cache
def get_mc_sentiment(mc, company, news_traceback, model):
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
                    'url': [article_urls[i]],
                }), ignore_index=True)
        except:
            pass

    mean_scores = news_scores.groupby('news_id').mean().reset_index()
    news_metadata = news_metadata.merge(mean_scores, on='news_id', how='inner')
    return news_metadata, news_scores

@st.cache
def get_et_sentiment(et, seoName, companyid, model):

    url = f'https://economictimes.indiatimes.com/{seoName}/stocksupdate/companyid-{companyid}.cms'
    r = requests.get(url)
    main_soup = BeautifulSoup(r.content, 'html.parser').find_all('div', {'class': 'eachStory'})
    nltk_downloader()
    model = SentimentIntensityAnalyzer()

    news_metadata = pd.DataFrame()
    news_scores = pd.DataFrame()
    for i,a in enumerate(main_soup):
        article_title = a.find('h3').text
        article_schedule = a.find('time').text[:-4]
        article_schedule = ' '.join(article_schedule.split(','))
        article_datetime = datetime.strptime(article_schedule, '%d %b %Y %I:%M%p')
        if a.find('a'):
            if '.cms' in a.find('a')['href']:
                article_url = 'https://economictimes.indiatimes.com' + a.find('a')['href']
                article_soup = BeautifulSoup(requests.get(article_url).content, 'html.parser')
                article_content = article_soup.find('div', {'class':'artText'})
                content_text_list = [x.strip() for x in article_content.text.split('\n') if x]

                for a_sentence in content_text_list:
                    x = pd.DataFrame(model.polarity_scores(a_sentence), index=range(1))
                    x['article_text'] = a_sentence
                    x['news_id'] = 'A' + str(i)
                    x = x[sorted(x.columns)]
                    news_scores = news_scores.append(x, ignore_index=True)

                news_metadata = news_metadata.append(pd.DataFrame({
                    'news_id': ['A' + str(i)],
                    'title': [article_title],
                    'datetime': [article_datetime.strftime('%Y-%m-%d %H:%M')],
                    'url': [article_url]
                }), ignore_index=True)
        else:

            content_text_list = [x.strip() for x in a.text.split('\n') if x]
            for a_sentence in content_text_list:
                x = pd.DataFrame(model.polarity_scores(a_sentence), index=range(1))
                x['article_text'] = a_sentence
                x['news_id'] = 'A' + str(i)
                x = x[sorted(x.columns)]
                news_scores = news_scores.append(x, ignore_index=True)

            news_metadata = news_metadata.append(pd.DataFrame({
                'news_id': ['A' + str(i)],
                'title': [article_title],
                'datetime': [article_datetime.strftime('%Y-%m-%d %H:%M')],
                'url': ['']
            }), ignore_index=True)

    mean_scores = news_scores.groupby('news_id').mean().reset_index()
    news_metadata = news_metadata.merge(mean_scores, on='news_id', how='inner')
    return news_metadata, news_scores


def app():

    st.title('News Sentiment Analysis')
    nltk_downloader()
    model = SentimentIntensityAnalyzer()

    mc = pd.read_csv('assets/mc_metadata.csv').drop('Unnamed: 0', axis=1)
    et = pd.read_csv('assets/et500urls.csv')

    # money control parameters
    company = st.sidebar.selectbox('MC Company Name', mc['name'].values)
    news_traceback = st.sidebar.selectbox('Duration', ['Last 30 days','Last 6 Months', '2021', '2020', '2019', '2018', '2017', '2015', '2014'], 2)

    # economic times parameters
    companyName = st.sidebar.selectbox('ET Company Name', et.title.values, 10)
    seoName = et.loc[et.title == companyName, 'seoName'].values[0]
    companyid = et.loc[et.title == companyName, 'companyid'].values[0]

    # split layout
    col1, col2 = st.beta_columns(2)

    # sentiment scores
    mc_meta, mc_scores = get_mc_sentiment(mc, company, news_traceback, model)
    et_meta, et_scores = get_et_sentiment(et, seoName, companyid, model)

    #  Pie in Column 1
    col1.header(f'Money Control Overall Sentiment in for {company}')
    col1.write('Share of Overall sentiment considering only positive and negative sentiments for MC Articles')
    overall_scores = mc_scores[['neg', 'pos']].mean().reset_index()
    overall_scores.columns = ['sentiment', 'score']
    fig = go.Figure(data=[go.Pie(labels=overall_scores.sentiment.values,
                                 values=overall_scores.score.values,
                                 hole=.5, marker_colors=['#F63366', '#079992'])]
                    )
    fig.update_layout(showlegend=False, font_size=14)
    fig.update_traces(textinfo='percent+label')
    col1.plotly_chart(fig)


    #  Pie in Column 2
    col2.header(f'Economic Times Overall Sentiment for {companyName}')
    col2.write('Share of Overall sentiment considering only positive and negative sentiments for ET articles')
    overall_scores = et_scores[['neg', 'pos']].mean().reset_index()
    overall_scores.columns = ['sentiment', 'score']
    fig = go.Figure(data=[go.Pie(labels=overall_scores.sentiment.values, values=overall_scores.score.values,
                                 hole=.5, marker_colors=['#F63366', '#079992']
                                 )])
    fig.update_layout(showlegend=False, font_size=14)
    fig.update_traces(textinfo='percent+label')
    col2.plotly_chart(fig)

    # tables
    st.header('Money Control')
    st.table(mc_meta.drop('url', axis=1))

    st.header('Economic Times')
    st.table(et_meta.drop('url', axis=1))
