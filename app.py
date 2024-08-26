import streamlit as st
import pandas as pd

# Load the dataset
data = pd.read_csv('customer_ranker.csv')

# Add a header
st.title("Interactive Customer Data for Customer Success")

# Custom sorting logic function for "Recently Sold Accounts" and "Aged Accounts"
def custom_sort(data, criteria):
    if criteria == "Recently Sold Accounts":
        return data.sort_values(by="time_since_last_order_days", ascending=False)
    elif criteria == "Aged Accounts":
        return data.sort_values(by="time_since_last_order_days", ascending=True)
    return data

# Create a toggle with custom sorting options
sort_criteria = st.radio(
    "Select sorting criteria:",
    ("Recently Sold Accounts", "Aged Accounts")
)

# Apply custom sorting logic based on the selected criteria
data_sorted_custom = custom_sort(data, sort_criteria)

# Apply secondary sorting by engagement_score
data_sorted_custom = data_sorted_custom.sort_values(by='engagement_score', ascending=False)

# Convert CustomerID to integer to remove decimal points
data_sorted_custom['CustomerID'] = data_sorted_custom['CustomerID'].astype(int).astype(str)

# Round `avg_` columns to no decimal places
avg_columns = [col for col in data_sorted_custom.columns if col.startswith("avg_")]
data_sorted_custom[avg_columns] = data_sorted_custom[avg_columns].round(0)

# Add dollar signs and round to no decimals for revenue columns
rev_columns = [col for col in data_sorted_custom.columns if 'rev' in col]
data_sorted_custom[rev_columns] = data_sorted_custom[rev_columns].applymap(lambda x: f"${x:,.0f}")

# Display the final sorted DataFrame
st.write("Sorted Customer Data:")
st.dataframe(data_sorted_custom, hide_index=True)
