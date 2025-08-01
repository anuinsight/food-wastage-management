
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- PostgreSQL Connection ---
def get_connection():
    return psycopg2.connect(
        dbname="food_wastage_db",
        user="postgres",
        password="Kirthu7625",
        host="localhost",
        port="5432"
    )

# --- Load Data ---
def load_data(table):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table};", conn)
    conn.close()
    return df

# --- Streamlit Title ---
st.title("🥦 Food Wastage Management Dashboard")
st.markdown("""
This project helps reduce local food waste by allowing providers to list surplus food items,
receivers to claim them, and track listings and claims efficiently.
""")

# --- Sidebar Navigation ---
menu = st.sidebar.selectbox("Navigation", [
    "📋 View Tables", "📊 Run Queries", "📈 Visualizations",
    "➕ Add Record", "✏️ Update Record", "🗑️ Delete Record", "👤 About"
])

# --- View Tables Section ---
if menu == "📋 View Tables":
    table = st.selectbox("Select Table", ["providers", "receivers", "food_listings", "claims"])
    df = load_data(table)
    st.dataframe(df)

# --- Run Queries Section ---
elif menu == "📊 Run Queries":
    st.subheader("📄 Run Predefined SQL Queries")
    query_options = {
        "Show all providers": "SELECT * FROM providers;",
        "Recent 10 claims (most recent first)": "SELECT * FROM claims ORDER BY timestamp DESC LIMIT 10;",
        "List food claimed status": "SELECT * FROM claims WHERE status = 'Claimed';",
        "Foods listed in current month": """
            SELECT * FROM food_listings
            WHERE DATE_TRUNC('month', listed_date) = DATE_TRUNC('month', CURRENT_DATE);
        """,
        "List of unclaimed food": """
            SELECT f.*
            FROM food_listings f
            LEFT JOIN claims c ON f.food_id = c.food_id
            WHERE c.food_id IS NULL;
        """,
        "Food items that expired": "SELECT * FROM food_listings WHERE expiry_date::date < CURRENT_DATE;",
        "Food and the receiver who claimed it": """
            SELECT f.food_name, r.name AS receiver_name, c.status, c.timestamp
            FROM claims c
            JOIN food_listings f ON c.food_id = f.food_id
            JOIN receivers r ON c.receiver_id = r.receiver_id;
        """,
        "Provider details with food items listed": """
            SELECT p.name, p.city, f.food_name, f.quantity, f.expiry_date
            FROM providers p
            JOIN food_listings f ON p.provider_id = f.provider_id;
        """
    }

    selected_query = st.selectbox("Choose a Query", list(query_options.keys()))
    query = query_options[selected_query]

    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error running query: {e}")

# --- Visualizations Section ---
elif menu == "📈 Visualizations":
    st.subheader("📊 Data Visualizations")
    viz_options = [
        "Claims per Day (line chart)",
        "Food Listings by Type (bar chart)",
        "Meal Type Distribution (pie chart)",
        "Top 5 Cities by Food Listings",
        "Claimed vs Unclaimed Food (pie chart)",
        "Most Claimed Food Item"
    ]
    selected_viz = st.selectbox("Choose Visualization", viz_options)
    conn = get_connection()

    if selected_viz == "Claims per Day (line chart)":
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        end_date = st.date_input("End Date", datetime.now())
        df = pd.read_sql(f"""
            SELECT DATE(timestamp) AS claim_date, COUNT(*) AS total_claims
            FROM claims
            WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY claim_date
            ORDER BY claim_date;
        """, conn)
        st.dataframe(df)
        fig = px.line(df, x='claim_date', y='total_claims', title='Claims Per Day')
        st.plotly_chart(fig)

    elif selected_viz == "Food Listings by Type (bar chart)":
        df = pd.read_sql("SELECT food_type, COUNT(*) AS total FROM food_listings GROUP BY food_type;", conn)
        st.dataframe(df)
        fig = px.bar(df, x='food_type', y='total', title='Food Listings by Type', color='food_type')
        st.plotly_chart(fig)

    elif selected_viz == "Meal Type Distribution (pie chart)":
        df = pd.read_sql("SELECT meal_type, COUNT(*) AS total FROM food_listings GROUP BY meal_type;", conn)
        st.dataframe(df)
        fig = px.pie(df, names='meal_type', values='total', title='Meal Type Distribution')
        st.plotly_chart(fig)

    elif selected_viz == "Top 5 Cities by Food Listings":
        df = pd.read_sql("""
            SELECT city, COUNT(*) AS total
            FROM providers
            JOIN food_listings ON providers.provider_id = food_listings.provider_id
            GROUP BY city
            ORDER BY total DESC
            LIMIT 5;
        """, conn)
        st.dataframe(df)
        fig = px.bar(df, x='city', y='total', title='Top 5 Cities by Listings', color='city')
        st.plotly_chart(fig)

    elif selected_viz == "Claimed vs Unclaimed Food (pie chart)":
        claimed = pd.read_sql("SELECT COUNT(*) AS total FROM claims;", conn).iloc[0]['total']
        total_food = pd.read_sql("SELECT COUNT(*) AS total FROM food_listings;", conn).iloc[0]['total']
        unclaimed = total_food - pd.read_sql("SELECT COUNT(DISTINCT food_id) AS total FROM claims;", conn).iloc[0]['total']
        df = pd.DataFrame({'Status': ['Claimed', 'Unclaimed'], 'Count': [claimed, unclaimed]})
        fig = px.pie(df, names='Status', values='Count', title='Claimed vs Unclaimed Food')
        st.plotly_chart(fig)

    elif selected_viz == "Most Claimed Food Item":
        df = pd.read_sql("""
            SELECT f.food_name, COUNT(*) AS total_claims
            FROM claims c
            JOIN food_listings f ON c.food_id = f.food_id
            GROUP BY f.food_name
            ORDER BY total_claims DESC
            LIMIT 1;
        """, conn)
        st.dataframe(df)
        fig = px.bar(df, x='food_name', y='total_claims', title='Most Claimed Food Item')
        st.plotly_chart(fig)

    conn.close()

# --- Add Record Placeholder ---
elif menu == "➕ Add Record":
    st.subheader("➕ Add New Record")
    table = st.selectbox("Select Table", ["providers", "receivers", "food_listings", "claims"])
    st.info(f"Form to insert data into `{table}` coming soon!")

# --- Update Record Placeholder ---
elif menu == "✏️ Update Record":
    st.subheader("✏️ Update Existing Record")
    st.info("Update feature is coming soon!")

# --- Delete Record Placeholder ---
elif menu == "🗑️ Delete Record":
    st.subheader("🗑️ Delete Record")
    st.info("Delete feature is coming soon!")

# --- About Section ---
elif menu == "👤 About":
    st.subheader("Project Info")
    st.markdown("""
**Project Title**: Local Food Waste Management  
**Created By**: Anupriya R  
**Skills Used**: Python, PostgreSQL, Streamlit, Plotly, SQL  
**Purpose**: Efficiently manage food donations and reduce wastage by matching donors and receivers.
""")

   





