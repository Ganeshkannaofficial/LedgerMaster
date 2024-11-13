import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Function to initialize session state
def init_session_state():
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'file_history' not in st.session_state:
        st.session_state.file_history = []

# Function to save uploaded CSV file to session state and maintain history
def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.file_history.append((timestamp, uploaded_file.name, st.session_state.df))

# Function to display raw data
def display_raw_data():
    if st.session_state.df is not None:
        st.write("Raw Data")
        st.write(st.session_state.df)

# Function to convert 'Date' column to datetime format
def convert_to_datetime():
    if st.session_state.df is not None and 'Date' in st.session_state.df.columns:
        st.session_state.df['Date'] = pd.to_datetime(st.session_state.df['Date'], dayfirst=True)

# Function to group data by 'Item Name' and calculate sales
def group_by_item_name():
    if st.session_state.df is not None and 'Item Name' in st.session_state.df.columns:
        item_sales = st.session_state.df.groupby('Item Name')['Amount'].sum().reset_index()
        st.write("Item Name-wise Sales Report")
        st.bar_chart(item_sales.set_index('Item Name'))

        # Save item-wise sales report
        if st.button('Download Item-wise Sales Report as CSV'):
            item_sales.to_csv('item_sales.csv', index=False)
            st.write("Item-wise Sales report saved as CSV file")

# Function to calculate month-wise turnover
def calculate_monthly_turnover():
    if st.session_state.df is not None and 'Date' in st.session_state.df.columns:
        df = st.session_state.df.copy()
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_turnover = df.groupby('Month')['Amount'].sum().reset_index()
        return monthly_turnover

# Function to visualize month-wise turnover with a square box chart
def visualize_monthly_turnover(monthly_turnover, attractiveness):
    if monthly_turnover is not None:
        fig = px.treemap(monthly_turnover, path=['Month'], values='Amount',
                         color='Amount',
                         color_continuous_scale='RdBu',
                         title='Month-wise Turnover',
                         hover_data={'Amount': ':,.2f'})
        fig.update_traces(textinfo="label+value")
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25),
                          uniformtext=dict(minsize=10, mode='hide'))
        fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
        fig.update_layout(height=500)
        fig.update_layout(autosize=True)
        st.plotly_chart(fig)

# Function to display upload history
def display_upload_history():
    if st.session_state.file_history:
        st.write("Upload History")
        for i, (timestamp, filename, df) in enumerate(st.session_state.file_history):
            st.write(f"Timestamp: {timestamp}, Filename: {filename}")
            if st.button(f"View {filename}", key=f"view_button_{i}"):
                st.write(df)
            if st.button(f"Download {filename}", key=f"download_button_{i}"):
                df.to_csv(f"downloaded_{filename}", index=False)
                st.write(f"{filename} downloaded")

# Main function
def main():
    init_session_state()

    st.title("Tally Prime Sales Register Financial Report")

    # Check if file is already uploaded, if not, display file uploader
    if st.session_state.df is None:
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        # Save uploaded file to session state
        save_uploaded_file(uploaded_file)

    # Sidebar menu for navigation
    menu = ["Raw Data", "Month-wise Turnover", "Item Name-wise Sales", "Upload History"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Convert 'Date' column to datetime format
    convert_to_datetime()

    # Display selected report based on menu choice
    if choice == "Raw Data":
        display_raw_data()
    elif choice == "Month-wise Turnover":
        monthly_turnover = calculate_monthly_turnover()
        if monthly_turnover is not None:
            attractiveness = st.slider("Attractiveness", min_value=0, max_value=10, value=5, step=1)
            visualize_monthly_turnover(monthly_turnover, attractiveness)
    elif choice == "Item Name-wise Sales":
        group_by_item_name()
    elif choice == "Upload History":
        display_upload_history()

if __name__ == "__main__":
    main()