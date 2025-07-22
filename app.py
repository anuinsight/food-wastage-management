import streamlit as st

st.title("Welcome to My Project")
st.write("This Project is about Local Food Waste Management")
st.slider("Pick a number", 0,100)
x = st.selectbox("Choose an option:", ["Option 1", "Option 2", "Option 3"])
st.write("You selected:", x)