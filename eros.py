import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Page config
st.set_page_config(page_title="Tokyo Stock Explorer", layout="wide")

# Styling
def remove_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: white;
            color: black;
        }
        .stApp > .main {
            background-color: rgba(255, 255, 255, 0.8);
        }
        h1, h2, h3, h4, h5, h6, p {
            color: black;
        }
        .stSidebar {
            background-color: rgba(255, 255, 255, 0.9);
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

remove_bg()

# App Title
st.title("📈 Tokyo Stock Price Explorer")
st.write("Explore major Japanese companies' stock prices or upload your own dataset.")

# Dates
start_date = datetime.datetime(2023, 4, 1)
end_date = datetime.datetime(2025, 4, 27)

# Sidebar: Dataset selection
st.sidebar.header("Data Source")
data_source = st.sidebar.radio("Choose data source:", ['Tokyo Stock Dataset', 'Upload CSV'])

# Load Tokyo Stock data
@st.cache_data(show_spinner=False)
def load_tokyo_data():
    companies = {
        'SONY': '6758.T',
        'TOYOTA': '7203.T',
        'HONDA': '7267.T',
        'MITSUBISHI CORP': '8058.T',
        'NISSAN MOTOR CORP': '7201.T',
        'NIPPON STEEL CORP': '5401.T',
        'HITACHI': '6501.T',
        'NINTENDO': '7974.T',
        'FUJITSU': '6702.T',
        'JAPAN AIRLINES': '9201.T'
    }

    frames = []
    for name, ticker in companies.items():
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            data = data.reset_index()
            data['Symbol'] = name
            frames.append(data)
        except Exception as e:
            st.warning(f"Failed to load {name}: {e}")
    
    df = pd.concat(frames, axis=0)
    df['Price_change'] = df['Close'] - df['Open']
    df['High_Low_Spread'] = df['High'] - df['Low']
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Load data based on user selection
if data_source == 'Tokyo Stock Dataset':
    with st.spinner("Loading Tokyo stock data..."):
        df = load_tokyo_data()
else:
    uploaded_file = st.sidebar.file_uploader("tokyo_index.csv", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        st.success("Custom dataset loaded!")
    else:
        st.info("Please upload a CSV file to continue.")
        st.stop()

# Symbol selection
st.sidebar.header("Stock Selection")
if 'Symbol' in df.columns:
    symbols = df['Symbol'].unique()
    selected_stock = st.sidebar.selectbox("Choose a stock:", symbols)
    df = df[df['Symbol'] == selected_stock]

# Date filtering
st.sidebar.header("Date Range Filter")
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
user_start = st.sidebar.date_input("Start date", min_value=min_date, max_value=max_date, value=min_date)
user_end = st.sidebar.date_input("End date", min_value=min_date, max_value=max_date, value=max_date)

df = df[(df['Date'].dt.date >= user_start) & (df['Date'].dt.date <= user_end)]

# Chart type
st.sidebar.header("Chart Type")
chart_type = st.sidebar.radio("Select chart type:", ['Static (Seaborn)', 'Interactive (Plotly)'])

# Download option
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

st.sidebar.download_button(
    label="Download current data as CSV",
    data=convert_df_to_csv(df),
    file_name='filtered_stock_data.csv',
    mime='text/csv',
)

# Main Chart Display
st.subheader(f"📊 Closing Price Trend")

if chart_type == 'Static (Seaborn)':
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x='Date', y='Close')
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.title(f"{selected_stock} Stock Price Over Time" if 'Symbol' in df.columns else "Stock Price Over Time")
    st.pyplot(fig)
else:
    fig = px.line(df, x='Date', y='Close', title="Stock Price Over Time (Interactive)")
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

# Show dataset
if st.checkbox("Show full dataset"):
    st.dataframe(df)
