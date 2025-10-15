# Retail Sales Dashboard
<br><br>
This project is an interactive **Retail Sales Dashboard** built using Streamlit and MySQL. It allows users to upload sales data in CSV or Excel format, cleans and processes the data, stores it in a MySQL database, and provides various analytics and visualizations to understand sales performance. The dashboard also enables filtering, trend analysis, and downloading of both data and visual charts for further reporting.
<br><br>
This project demonstrates:<br>
- Building interactive dashboards using Streamlit<br>
- Data cleaning and preprocessing with Pandas<br>
- Storing and retrieving data from a MySQL database<br>
- Generating dynamic charts using Matplotlib<br>
- File handling and export (CSV/Excel/PNG)<br>
- Basic metrics computation and year-over-year growth analysis<br>
- User-friendly UI with sidebar filters and tabs for visualization<br>
<br><br>
## Features<br>
- **Upload Data**: Users can upload sales datasets in CSV or Excel format. The data is previewed immediately on the dashboard.<br>
- **Data Cleaning**: Automatic cleaning of column names, conversion of numeric columns, date parsing, removal of duplicates, and handling of missing critical data like Address or Order Quantity.<br>
- **Revenue Calculation**: Total revenue is calculated from the "Total" column and stored as a new column `revenue`.<br>
- **Date Feature Engineering**: Generates additional date-related columns including year, month, month name, quarter, and year-month combination.<br>
- **Database Storage**: Cleaned data is stored in a MySQL database (`sales_final_db`) and table (`sales`) for persistent storage. Data insertion is done in chunks for efficiency.<br>
- **Metrics Dashboard**: Displays key performance indicators (KPIs) like total revenue, total orders, average order value, and yearly growth percentage.<br>
- **Filtering Options**: Sidebar filters allow users to filter data by year, month, or specific date range.<br>
- **Interactive Charts**:<br>
  - **Monthly Revenue Trend**: Line chart showing revenue trend month-wise.<br>
  - **Top Products**: Horizontal bar chart showing the top 10 products by revenue.<br>
  - **State-wise Revenue**: Bar chart showing revenue distribution by state.<br>
- **Export Options**: Filtered datasets can be downloaded as CSV or Excel. Charts can also be downloaded as PNG images.<br>
- **Responsive Design**: Layout automatically adjusts with wide-screen configuration for better visualization.<br>
<br><br>
## Code Walkthrough & Function Descriptions
<br><br>
### Database Connection<br>
```python<br>
@st.cache_resource<br>
def get_connection():<br>
    return mysql.connector.connect(<br>
        host="localhost",<br>
        user="root",<br>
        password="123",<br>
        database="sales_final_db"<br>
    )
```
- Uses st.cache_resource to avoid reconnecting on every run.<br>
- Establishes a connection to MySQL database.
<br><br>
#Data Upload and Preview
<br>
- The uploaded data is previewed using st.dataframe.
<br>
- Users can upload CSV or Excel files via st.file_uploader.
<br>
- If the database table exists, it truncates previous data before inserting new rows.
<br><br>
#Data Cleaning (clean(df))
<br>
- Strips whitespaces from column names.
<br>
- Converts numeric and money columns to proper numeric types.
<br>
- Parses Order Date into datetime objects and creates additional columns for analysis.
<br>
- Removes duplicate rows and rows with missing critical data.
<br>
- Computes unit_price as revenue divided by order quantity.
<br><br>
#Data Loading<br>
@st.cache_data<br>
def load_data():<br>
    query = "SELECT * FROM sales"<br>
    return pd.read_sql(query, conn)
<br>
- Fetches cleaned data from the database.
<br>
- Uses caching to improve performance for repeated queries.
<br><br>
#Metrics Calculation
<br>
- Total Revenue: Sum of revenue column.
<br>
- Total Orders: Count of orders.
<br>
- Average Order Value: Total revenue divided by total orders.
<br>
- Yearly Growth: Percentage growth compared to previous year.
<br><br>
#Sidebar Filters
<br>
- Select Year and Month to filter data dynamically.
<br>
- Choose a date range using a date picker to analyze specific periods.
<br><br>
#Download Filtered Data
<br>
- Filtered datasets can be exported as CSV or Excel.
<br>
- Charts for monthly trends, top products, and state revenue can be downloaded as PNG files.
<br><br>
#Visualizations
<br>
1. Monthly Trend: Line chart with markers showing month-wise revenue.
<br>
2. Top Products: Horizontal bar chart showing top 10 products by revenue.
<br>
3. State-wise Revenue: Bar chart showing top 10 states by revenue.
<br><br>
#Tabs
<br>
- Visualizations are organized in three tabs for a clean, navigable dashboard interface:
<br>
1. Monthly Trend
<br>
2. Top Products
<br>
3. State-wise Revenue
<br><br>
#How to Run
<br>
1. Ensure MySQL is installed and running.
<br>
2. Update the MySQL credentials in app.py (host, user, password).
<br>
3. Install required Python libraries:
<br>
pip install streamlit pandas matplotlib mysql-connector-python xlsxwriter openpyxl
<br>
4. Run the Streamlit app:
<br>
streamlit run app.py
<br>
5. Open the local URL provided by Streamlit and upload your sales dataset.
<br>
6. Use sidebar filters to analyze data and download reports or charts as needed.
<br><br>
#Future Improvements
<br>
- Add user authentication to restrict access to authorized personnel.
<br>
- Include interactive visualizations using Plotly for better insights.
<br>
- Implement historical comparison with rolling trends and YoY/ MoM growth charts.
<br>
- Add predictive analytics for sales forecasting.
<br>
- Enhance dashboard with more metrics like top customers, order priority analysis, and profit margin trends.
<br><br>
#Credits
<br>
- Developed by Ritika Bhasin, IT Student, IPU '28.
<br>
- Built using Streamlit, Pandas, Matplotlib, and MySQL.
<br>
- Inspired by real-world retail analytics requirements for interactive sales monitoring.
