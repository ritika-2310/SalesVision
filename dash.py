import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import mysql.connector
import io
from io import BytesIO
from IPython.display import display
import numpy as np
from datetime import date

#database connection
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="sales_final_db"
    )
conn = get_connection()
cursor = conn.cursor()

#page configuration
st.set_page_config(page_title="retail sales dashboard",layout="wide")
st.title("retail sales dashboard")

uploaded_file = st.file_uploader("choose a file",type=['csv','xlsx'])
if uploaded_file is not None:
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sales (
    `Order No` VARCHAR(50),
    `Order Date` DATE,
    `Customer Name` VARCHAR(100),
    `Address` VARCHAR(255),
    `City` VARCHAR(100),
    `State` VARCHAR(100),
    `Customer Type` VARCHAR(50),
    `Account Manager` VARCHAR(100),
    `Order Priority` VARCHAR(20),
    `Product Name` VARCHAR(150),
    `Product Category` VARCHAR(100),
    `Product Container` VARCHAR(100),
    `Ship Mode` VARCHAR(50),
    `Ship Date` DATE,
    `Cost Price` FLOAT,
    `Retail Price` FLOAT,
    `Profit Margin` FLOAT,
    `Order Quantity` INT,
    `Sub Total` FLOAT,
    `Discount %` FLOAT,
    `Discount $` FLOAT,
    `Order Total` FLOAT,
    `Shipping Cost` FLOAT,
    `Total` FLOAT,
    `revenue` FLOAT,
    `year` INT,
    `month` INT,
    `month_name` VARCHAR(20),
    `ym` VARCHAR(20),
    `quarter` VARCHAR(10),
    `unit_price` FLOAT
    );
    """
    cursor.execute(create_table_query)
    cursor.execute("TRUNCATE TABLE sales")
    conn.commit()
    st.success("file uploaded successfully")
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.write("preview of uploaded data : ")
    st.dataframe(df.head())

#load data from file and clean it

def clean(df):
    # Strip column names
    df.columns = df.columns.str.strip()

    # Revenue from Total
    if 'Total' in df.columns:
        df['revenue'] = pd.to_numeric(
            df['Total'].astype(str).str.replace(r'[^0-9.\-]', '', regex=True),
            errors='coerce'
        )

    # Parse dates once
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df['year'] = df['Order Date'].dt.year
        df['month'] = df['Order Date'].dt.month
        df['month_name'] = df['Order Date'].dt.strftime('%b')
        df['ym'] = df['Order Date'].dt.to_period('M').astype(str)
        df['quarter'] = df['Order Date'].dt.to_period('Q').astype(str)

    # Strip only object/string columns
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

    # Convert numeric/money columns
    money_col = ['Cost Price','Retail Price','Profit Margin','Order Total','Sub Total',
                 'Shipping Cost','Discount %','Discount $','Order Quantity','Total']
    for col in money_col:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r'[^0-9.\-]', '', regex=True),
                errors='coerce'
            )

    # Drop duplicates
    df = df.drop_duplicates()

    # Drop rows with missing critical info
    df = df.dropna(subset=['Address','Order Quantity'])

    # Calculate unit price
    df['unit_price'] = df['revenue'] / df['Order Quantity']

    return df

if uploaded_file is not None:
    df = clean(df)
    #data loading in mysql 
    cursor.execute("CREATE DATABASE IF NOT EXISTS sales_final_db")
    cursor.execute("USE sales_final_db")
    print("databse created sales_final_db and selected")
    #Create table with exact same columns as your CSV with same order
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sales (
    `Order No` VARCHAR(50),
    `Order Date` DATE,
    `Customer Name` VARCHAR(100),
    `Address` VARCHAR(255),
    `City` VARCHAR(100),
    `State` VARCHAR(100),
    `Customer Type` VARCHAR(50),
    `Account Manager` VARCHAR(100),
    `Order Priority` VARCHAR(20),
    `Product Name` VARCHAR(150),
    `Product Category` VARCHAR(100),
    `Product Container` VARCHAR(100),
    `Ship Mode` VARCHAR(50),
    `Ship Date` DATE,
    `Cost Price` FLOAT,
    `Retail Price` FLOAT,
    `Profit Margin` FLOAT,
    `Order Quantity` INT,
    `Sub Total` FLOAT,
    `Discount %` FLOAT,
    `Discount $` FLOAT,
    `Order Total` FLOAT,
    `Shipping Cost` FLOAT,
    `Total` FLOAT,
    `revenue` FLOAT,
    `year` INT,
    `month` INT,
    `month_name` VARCHAR(20),
    `ym` VARCHAR(20),
    `quarter` VARCHAR(10),
    `unit_price` FLOAT
    );
    """
    cursor.execute(create_table_query)
    print("\nTable 'sales' created.")
    #insert data from csv to mysql
    cols = ','.join([f"`{col}`" for col in df.columns])
    placeholder = ','.join(["%s"]*len(df.columns))
    insert_query = f"INSERT INTO sales({cols}) VALUES ({placeholder})"
    #convert all nans to none in mysql and also all data into rows of numpy
    data_tuple = [tuple(None if pd.isna(val) else val for val in row) for row in df.to_numpy()] #sublists in lists
    #insertion in chunks should be done like insert 500 rows first then another 500 rows till then 1000 would be inserted continue with gap of 500 rows each time
    for i in range(0,len(data_tuple),500):
        cursor.executemany(insert_query,data_tuple[i:i+500])
        conn.commit()
    print("\nall data inserted successfully.")

#data loading
@st.cache_data
def load_data():
    query = """SELECT * FROM  sales"""
    return pd.read_sql(query,conn)
if uploaded_file is not None:
    df = load_data()
    st.success(f"Number of rows loaded from database: {len(df)}")
else:
    df = load_data()

#4th column metric
# Convert date column
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
# Yearly revenue
yearly_revenue = df.groupby('Year')['revenue'].sum().sort_index()
# Calculate YoY Growth (%)
yoy_growth = yearly_revenue.pct_change().fillna(0) * 100
# Latest year comparison
latest_year = yearly_revenue.index.max()
prev_year = latest_year - 1
#latest_revenue = yearly_revenue[str(latest_year)]
latest_revenue = yearly_revenue.get(latest_year, 0)
previous_revenue = yearly_revenue.get(prev_year, 0)
growth_percent = ((latest_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue != 0 else 0

#sidebar filters
st.sidebar.header("filters")
year_list = sorted(df['year'].dropna().unique())
selected_year = st.sidebar.selectbox("select year",options = ["all"]+[str(y) for y in year_list])
if selected_year!="all":
    df = df[df['year']==int(selected_year)]
month_list = sorted(df['month_name'].dropna().unique())
selected_month = st.sidebar.selectbox("select month",options = ["all"]+[str(y) for y in month_list])
if selected_month!="all":
    df = df[df['month_name']==selected_month]
total_revenue = df['revenue'].sum()
total_orders = len(df)
avg_order_value = total_revenue/total_orders if total_orders > 0 else 0

#metrics
col1,col2,col3,col4 = st.columns(4)
col1.metric("total revenue",f"${total_revenue:,.2f}")
col2.metric("total orders",total_orders)
col3.metric("average value order",f"${avg_order_value:,.2f}")
col4.metric("yearly growth",f"{growth_percent:.2f}%")

st.sidebar.subheader("filter by date range")
min_date = pd.to_datetime(df['Order Date']).min()
max_date = pd.to_datetime(df['Order Date']).max()
# Convert to Python date, with fallback if NaT
if pd.isna(min_date):
    min_date = date.today()
else:
    min_date = min_date.date()

if pd.isna(max_date):
    max_date = date.today()
else:
    max_date = max_date.date()

date_range = st.sidebar.date_input("select date range",value=(min_date,max_date),min_value = min_date,max_value = max_date) #use tuple not list
# Safely unpack
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range
df = df[(pd.to_datetime(df['Order Date'])>=pd.to_datetime(start_date)) & (pd.to_datetime(df['Order Date'])<=pd.to_datetime(end_date))]

st.markdown("-----export filtered data")
csv = df.to_csv(index=False).encode('utf-8') #convert to csv
#convert to excel
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer,engine='xlsxwriter') as writer:
    df.to_excel(writer,index=False,sheet_name='filtered_data')
excel_data = excel_buffer.getvalue()

#download buttons
col_a, col_b = st.columns(2)
with col_a:
    st.download_button(
        label = "download as CSV",
        data = csv,
        file_name='filtered_data.csv',
        mime='csv/text'
    )
with col_b:
    st.download_button(
        label = "download as xlsx",
        data = excel_data,
        file_name='filtered_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' #
    )

#charts to be made in 3 different tabs
tab1,tab2,tab3 = st.tabs(['monthly trend','top products','state wise revenue'])
#monthly trend
with tab1:
    monthly = df.groupby('month_name')['revenue'].sum().reindex(month_list)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(monthly.index,monthly.values,marker='o')
    ax.set_title("monthly revenue trend")
    ax.set_xlabel("month")
    ax.set_ylabel("revenue")
    st.pyplot(fig)
    #save chart to buffer
    buf = BytesIO()
    fig.savefig(buf,format='png')
    st.download_button(
        label = "download chart as png",
        file_name = 'monthly_trend.png',
        data = buf.getvalue(),
        mime='image/png'
    )
with tab2:
    top_products = df.groupby('Product Name')['revenue'].sum().sort_values(ascending=False).head(10)
    fig,ax = plt.subplots(figsize=(8,5))
    ax.barh(top_products.index[::-1],top_products.values[::-1])
    ax.set_title("top 10 products by revenue")
    st.pyplot(fig)
    #save chart to buffer
    buf = BytesIO()
    fig.savefig(buf,format='png')
    st.download_button(
        label = "download chart as png",
        file_name = 'top_products.png',
        data = buf.getvalue(),
        mime='image/png'
    )
with tab3:
    state_rev = df.groupby('State')['revenue'].sum().sort_values(ascending=False).head(10)
    fig,ax = plt.subplots(figsize=(8,5))
    ax.bar(state_rev.index,state_rev.values)
    ax.set_title("revenue by state")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    #save chart to buffer
    buf = BytesIO()
    fig.savefig(buf,format='png')
    st.download_button(
        label = "download chart as png",
        file_name = 'state_revenue.png',
        data = buf.getvalue(),
        mime='image/png'
    )

st.markdown("----")
st.caption("<div style='text-align:center;color:gray;'>""© 2025 Retail Sales Analytics Built with Streamlit & MySQL""</div>",unsafe_allow_html=True)