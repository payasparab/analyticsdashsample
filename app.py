import streamlit as st
import pandas as pd

# Load the dataset
data = pd.read_csv('customer_ranker.csv')

# Add a header
st.title("Interactive Customer Ranker")

# Create a toggle with custom sorting options
st.header('Sorting Criteria')

st.header('Quick Filters')
# Apply checkbox filters first
filtered_data = data.copy()

recurring_orders = st.checkbox("Show only recurring customers (num_orders > 1)")
multiple_items = st.checkbox("Show only customers with multiple unique items (num_unique_items_bought > 1)")


# Start with the full dataset
filtered_data = data.copy()

# Build combined conditions
conditions = []

if recurring_orders:
    conditions.append(filtered_data['num_orders'] > 1)

if multiple_items:
    conditions.append(filtered_data['num_unique_items_bought'] > 1)

# Apply all conditions at once
if conditions:
    combined_condition = conditions[0]
    for condition in conditions[1:]:
        combined_condition &= condition
    filtered_data = filtered_data[combined_condition]

# Add sliders for numerical filters
num_orders_range = st.slider("Number of Orders", int(data['num_orders'].min()), int(data['num_orders'].max()), (int(data['num_orders'].min()), int(data['num_orders'].max())))
avg_rev_per_order_range = st.slider("Average Revenue per Order", float(data['avg_rev_per_order'].min()), float(data['avg_rev_per_order'].max()), (float(data['avg_rev_per_order'].min()), float(data['avg_rev_per_order'].max())))
# Add sliders for numerical filters including the relationship length
relationship_length_range = st.slider(
    "Relationship Length (days)", 
    int(data['relationship_length_days'].min()), 
    int(data['relationship_length_days'].max()), 
    (int(data['relationship_length_days'].min()), int(data['relationship_length_days'].max()))
)

time_since_last_order_range = st.slider("Time Since Last Order (days)", int(data['time_since_last_order_days'].min()), int(data['time_since_last_order_days'].max()), (int(data['time_since_last_order_days'].min()), int(data['time_since_last_order_days'].max())))

# Apply slider filters after checkbox filters
filtered_data = filtered_data[
    (filtered_data['num_orders'] >= num_orders_range[0]) & (filtered_data['num_orders'] <= num_orders_range[1]) &
    (filtered_data['avg_rev_per_order'] >= avg_rev_per_order_range[0]) & (filtered_data['avg_rev_per_order'] <= avg_rev_per_order_range[1]) &
    (filtered_data['time_since_last_order_days'] >= time_since_last_order_range[0]) & (filtered_data['time_since_last_order_days'] <= time_since_last_order_range[1])
]

filtered_data = filtered_data[
    ((filtered_data['relationship_length_days'] >= relationship_length_range[0]) & 
     (filtered_data['relationship_length_days'] <= relationship_length_range[1])) | 
    (filtered_data['relationship_length_days'].isna())
]

# Apply secondary sorting by engagement_score
data_sorted_custom =  filtered_data.sort_values(by=['engagement_score', 'total_net_rev'], ascending=[False, False])

# Convert CustomerID to integer to remove decimal points
data_sorted_custom['CustomerID'] = data_sorted_custom['CustomerID'].astype(int).astype(str)

# Round `avg_` columns to no decimal places
avg_columns = [col for col in data_sorted_custom.columns if col.startswith("avg_")]
data_sorted_custom[avg_columns] = data_sorted_custom[avg_columns].round(0)

# Add dollar signs and round to no decimals for revenue columns
rev_columns = [col for col in data_sorted_custom.columns if 'rev' in col]
data_sorted_custom[rev_columns] = data_sorted_custom[rev_columns].applymap(lambda x: f"${x:,.0f}")

display_cols = [
    'CustomerID', 
    'engagement_score', 
    'total_net_rev', 
    'num_orders', 
    'avg_rev_per_order',
    'num_unique_items_bought', 
    'relationship_length_days',
    'time_since_last_order_days'
]

data_display = data_sorted_custom[display_cols]
data_display.columns = [
    'CustomerID',
    'Engage Score',
    'Total Lifetime Revenue',
    '# of Orders', 
    'Avg Rev Per Order',
    'Unique Items Purchased',
    'Length of Relationship', 
    'Days Since Last Order'
]

# Function to convert DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

## Add some data around the current XS of data
# Display the number of customers matching the criteria
num_customers = data_sorted_custom['CustomerID'].nunique()
st.metric(label="Number of Customers Matching Criteria", value=num_customers)

# Create a list to store descriptions of applied filters
applied_filters = []

# Checkbox filters
if recurring_orders:
    applied_filters.append("Recurring customers (num_orders > 1)")
if multiple_items:
    applied_filters.append("Customers with multiple unique items (num_unique_items_bought > 1)")

# Slider filters
applied_filters.append(f"Number of Orders between {num_orders_range[0]} and {num_orders_range[1]}")
applied_filters.append(f"Avg Revenue per Order between ${avg_rev_per_order_range[0]:,.0f} and ${avg_rev_per_order_range[1]:,.0f}")
applied_filters.append(f"Time Since Last Order between {time_since_last_order_range[0]} and {time_since_last_order_range[1]} days")
applied_filters.append(f"Relationship Length between {relationship_length_range[0]} and {relationship_length_range[1]} days")

# Display the applied filters as a list
st.text("Filters Applied:")
st.write(", ".join(applied_filters))

# Display the total number of customers covered by the current cut of data
total_customers = data['CustomerID'].nunique()
percentage_customers = (num_customers/total_customers) * 100
st.write(f"Isolating {num_customers} accounts from {total_customers} total customers or {percentage_customers:.2f}%")


# Display the final sorted DataFrame
st.write("Sorted Customer Data:")
st.dataframe(
    data_display, 
    hide_index=True,  
    use_container_width=True
)

# Create a download button
csv = convert_df_to_csv(data_display)
st.download_button(
    label="Download Customer List as CSV",
    data=csv,
    file_name='customer_list.csv',
    mime='text/csv',
)