import base64
from PIL import Image
import plotly.graph_objects as go

def get_table_download_link(df, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">{text}</a>'
    return href

def show_logo():
    logo = Image.open('assets/logo.png')
    return logo

def plot_indicators(value,text,width, height):
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="delta",
        value=value,
        title=text,
        delta={'reference': 0, 'relative': False, "font": {"size": 60}},
        domain={'x': [0, 0], 'y': [0, 0]}))
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        width=width,
        height=height,
        # paper_bgcolor='rgba(0,0,0,0.05)',
        # plot_bgcolor='rgba(0,0,0,0.05)',
    )
    return fig

