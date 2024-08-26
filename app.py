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

# Add filters for recurring orders and multiple unique items
recurring_orders = st.checkbox("Show only recurring orders (num_orders > 0)")
multiple_items = st.checkbox("Show only customers with multiple unique items (num_unique_items_bought > 1)")

# Add sliders for numerical filters
avg_rev_per_order_range = st.slider("Average Revenue per Order", float(data['avg_rev_per_order'].min()), float(data['avg_rev_per_order'].max()), (float(data['avg_rev_per_order'].min()), float(data['avg_rev_per_order'].max())))
relationship_length_range = st.slider("Relationship Length (days)", int(data['relationship_length_days'].min()), int(data['relationship_length_days'].max()), (int(data['relationship_length_days'].min()), int(data['relationship_length_days'].max())))
time_since_last_order_range = st.slider("Time Since Last Order (days)", int(data['time_since_last_order_days'].min()), int(data['time_since_last_order_days'].max()), (int(data['time_since_last_order_days'].min()), int(data['time_since_last_order_days'].max())))

# Apply filters
filtered_data = data[
    (data['avg_rev_per_order'] >= avg_rev_per_order_range[0]) & (data['avg_rev_per_order'] <= avg_rev_per_order_range[1]) &
    (data['relationship_length_days'] >= relationship_length_range[0]) & (data['relationship_length_days'] <= relationship_length_range[1]) &
    (data['time_since_last_order_days'] >= time_since_last_order_range[0]) & (data['time_since_last_order_days'] <= time_since_last_order_range[1])
]

if recurring_orders:
    filtered_data = filtered_data[filtered_data['num_orders'] > 0]

if multiple_items:
    filtered_data = filtered_data[filtered_data['num_unique_items_bought'] > 1]

# Apply custom sorting logic based on the selected criteria
data_sorted_custom = custom_sort(filtered_data, sort_criteria)

# Apply secondary sorting by engagement_score
data_sorted_custom = data_sorted_custom.sort_values(by=['time_since_last_order_days', 'engagement_score'], ascending=[sort_criteria == "Aged Accounts", False])

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
st.dataframe(
    data_sorted_custom, 
    hide_index=True,  
    use_container_width=True
)