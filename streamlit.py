import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
import plotly.express as px

# Load the merged data from the CSV file
merged_data = pd.read_csv("segmented_wholesale.csv")

retail_data = pd.read_csv("segmented_retail.csv")

# Set page title and configure layout
st.set_page_config(page_title='SAKA Customer Segmentation', layout='wide')

# Add the image to the sidebar
st.sidebar.image('SAKA-Logo.png', use_column_width=False)

st.markdown("""
<style>
.center {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 5vh;
    flex-direction: column;
    gap: 20px; /* Add space between elements */
}
</style>
""", unsafe_allow_html=True)

# Center-align text using HTML tags
st.write('<div class="center"><h1>SAKA</h1></div>', unsafe_allow_html=True)
st.write("----")

# Define sidebar
st.sidebar.title('Menu')

########################################################################################################################

grouped_data = merged_data.groupby('Name').agg({
    'Segment': 'first',
    'Sales_Amount': 'sum',  # Aggregate sales amount by summing
    'Frequency': 'max'  
}).reset_index()

grouped_data_r = retail_data.groupby('Name').agg({
    'Segment': 'first',
    'Sales_Amount': 'sum',  # Aggregate sales amount by summing
    'Frequency': 'max'  # Take the maximum frequency
}).reset_index()

def plot_segment_distribution(data):
    fig = px.histogram(data, x="Segment", labels={"Segment": "Customer Segment"})
    
    # Customize the appearance and interactivity
    fig.update_traces(marker_color='lightskyblue', marker_line_color='darkblue',
                      marker_line_width=1.5, opacity=0.7)
    fig.update_layout(bargap=0.3, xaxis_title="Customer Segment", yaxis_title="Count",
                      hovermode="closest")
    
    return fig

########################################################################################################################



def main():
    # Add tabs to the app
    tabs = ["Home", "Raw Data", "Customer Segment Distribution", "Average Spend by Segment","Brand Analysis","Recommendations"]
    selected_tab = st.sidebar.selectbox("Select a tab:", tabs)

    if selected_tab == "Home":
        # Display title and description on the home tab
        st.image("Banner.jpg")#, width=1000, use_column_width=False
        st.subheader('''SAKA is a market-driven company that markets and distributes an extensive portfolio of *tires*, *batteries*, *lubricants*, *garage equipment* & *accessories* with offices in Europe, Middle East and Africa. They cater to 300+ tire service centers, fleets & companies in Lebanon.In addition, our offshore operations entail business with subsidiaries and sister companies in several African and MENA countries.''')


    elif selected_tab == "Raw Data":
        # Display the raw data table only
        st.subheader("Raw Data")
        st.write(merged_data)  # Display the DataFrame as a table

#33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

    elif selected_tab == "Customer Segment Distribution":
    
        unique_customers = merged_data.drop_duplicates(subset=["Name", "Segment"])
    # Split the layout into two columns
        col1, col2 = st.columns(2)
    
    # Column 1: Display the bar graph
        with col1:
            st.subheader("Customer Segment Distribution")
            plot_container = st.container()
            with plot_container:
                st.plotly_chart(plot_segment_distribution(grouped_data), use_container_width=False, width=700)

            st.subheader("Find Customer Segment")
            customer_name = st.text_input("Enter Customer Name:")
            if customer_name:
                matching_data = grouped_data.loc[grouped_data["Name"].str.contains(customer_name, case=False)]
                if not matching_data.empty:
                    selected_segment = matching_data["Segment"].iloc[0]
                    total_sales = matching_data["Sales_Amount"].iloc[0]
                    frequency = matching_data["Frequency"].iloc[0]  # Since there's only one row per customer in grouped_data_r

                    st.write(f"Segment: {selected_segment}")
                    st.write(f"Total Sales: {total_sales:.2f}")
                    st.write(f"Frequency: {frequency}")
                else:
                    st.write("Customer not found.")
        
        # Column 2: Show unique customers in each segment
        with col2:
            st.subheader("Unique Customers in Each Segment")
            
            # Calculate unique customers in each segment
            unique_customers = merged_data.drop_duplicates(subset=["Name", "Segment"])
            
            # Order select box options from low to high
            ordered_segments = unique_customers["Segment"].sort_values(ascending=True).unique()
            selected_segment = st.selectbox("Select a Segment:", ordered_segments)
            
            # Display segment and list of unique customers in a DataFrame
            # st.write(f"Segment: {selected_segment}")
            st.write("Customers:")
            
            # Filter and display unique customers for the selected segment
            segment_customers = unique_customers[unique_customers["Segment"] == selected_segment]
            st.dataframe(segment_customers, width=800)

#44444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444

    elif selected_tab == "Average Spend by Segment":
        
        # Split the layout into two columns
        col1, col2 = st.columns(2)
        segment_order = ["Low-Value", "Medium-Value", "High-Value"]
        # Column 1: Spending Pattern Visualization
        with col1:
            with st.container():
                st.subheader("Average Spend by Segment")
            
                # Create a radio button to toggle between viewing by individual months and viewing over all months
                view_option = st.radio("View Option", ["All Months","Individual Months"])
            
                if view_option == "Individual Months":
                    
                    months = merged_data["Month"].unique()
                    sorted_months = ["Jan", "Feb", "Mar", "April", "May", "June"]
                    selected_months = st.multiselect("Select Months", sorted_months, default=sorted_months)

                    # Convert the "Month" column to a categorical data type with custom ordering
                    month_order = pd.CategoricalDtype(categories=sorted_months, ordered=True)
                    filtered_data = merged_data[merged_data["Month"].isin(selected_months)]
                    filtered_data["Month"] = filtered_data["Month"].astype(month_order)

                    # Filter data based on selected months
                    filtered_data = merged_data[merged_data["Month"].isin(selected_months)]

                    # Calculate average spend per segment and month
                    avg_spend_per_segment_month = filtered_data.groupby(["Segment", "Month"]).apply(
                        lambda group: group["Sales_Amount"].sum() / group["Name"].nunique()
                    ).reset_index(name="Average_Spend")

                    # Define the order of segments for the x-axis
                    segment_order = ["Low-Value", "Medium-Value", "High-Value"]

                    # Create a bar chart using Plotly Express
                    # Create a bar chart using Plotly Express
                    fig_avg_spend_month = px.bar(
                        avg_spend_per_segment_month,
                        x="Segment",
                        y="Average_Spend",
                        color="Month",
                        barmode="group",  # Use "group" mode for grouped bars
                        category_orders={"Segment": segment_order, "Month": sorted_months},  # Set the category order
                        labels={"Segment": "Segment", "Average_Spend": "Average Spend ($)", "Month": "Month"},
                        title="Average Spend by Segment per Month"
                    )

                    # Customize the appearance
                    fig_avg_spend_month.update_traces(marker_line_width=1.5, opacity=0.7)
                    fig_avg_spend_month.update_layout(xaxis_title="Segment", yaxis_title="Average Spend ($)", height=600)

                    # Display the bar chart
                    st.plotly_chart(fig_avg_spend_month, use_container_width=True)
                else:

                    avg_spend_per_segment = merged_data.groupby("Segment").apply(
                        lambda group: group["Sales_Amount"].sum() / group["Name"].nunique()
                    ).reset_index(name="Average_Spend")
                    
                    # Create a bar chart using Plotly Express
                    fig_avg_spend = px.bar(
                        avg_spend_per_segment,
                        x="Segment",
                        y="Average_Spend",
                        color="Segment",
                        category_orders={"Segment": segment_order},  # Set the category order
                        labels={"Segment": "Segment", "Average_Spend": "Average Spend"},
                        title="Average Spend by Segment Over Q1 & Q2"
                    )
                    
                    # Customize the appearance
                    fig_avg_spend.update_traces(marker_line_width=1.5, opacity=0.7)
                    fig_avg_spend.update_layout(xaxis_title="Segment", yaxis_title="Average Spend",height=600)
                    
                    # Display the bar chart
                    st.plotly_chart(fig_avg_spend, use_container_width=True)

        # Column 2: Top Customers by Segment
        with col2:
            st.subheader("Top Customers by Segment")
            
            # Calculate total spending per customer and segment
            total_spending_per_customer = merged_data.groupby(["Segment", "Name"])["Sales_Amount"].sum().reset_index()
            
            # Get the top customers by segment based on total spending
            top_customers_per_segment = total_spending_per_customer.groupby("Segment").apply(
                lambda group: group.nlargest(10, "Sales_Amount")
            ).reset_index(drop=True)
            
            # Create a filter to select the number of customers to display
            num_customers = st.number_input("Select Number of Customers to Display:", min_value=1, max_value=len(top_customers_per_segment),value=5)
            
            # Limit the number of customers based on the filter selection
            top_customers_filtered = top_customers_per_segment.groupby("Segment").head(num_customers)
            
            # Create a bar chart to visualize top customers by segment
            fig_top_customers = px.bar(
                top_customers_filtered,
                x="Name",
                y="Sales_Amount",
                color="Segment",
                category_orders={"Segment": segment_order},  # Set the category order
                labels={"Name": "Customer Name", "Sales_Amount": "Total Spending"},
                title=f"Top {num_customers} Customers by Segment"
            )
            
            # Customize the appearance
            fig_top_customers.update_traces(marker_line_width=1.5, opacity=0.7)
            fig_top_customers.update_layout(xaxis_title="Customer Name", yaxis_title="Total Spending ($)", height=600)
            
            # Display the bar chart
            st.plotly_chart(fig_top_customers, use_container_width=True)
    
#5555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555

    elif selected_tab == "Brand Analysis":
        segment_order = ["Low-Value", "Medium-Value", "High-Value"]
        st.subheader("Brand Analysis")
        
        # Create a filter for selecting a specific segment
        selected_segment = st.selectbox("Select a Segment:", segment_order)
        
        # Create a filter for selecting an item category
        item_categories = merged_data["Item Category"].unique()
        selected_category = st.selectbox("Select an Item Category:", item_categories)
        
        # Filter data based on selected segment and category
        segment_category_data = merged_data[(merged_data["Segment"] == selected_segment) & (merged_data["Item Category"] == selected_category)]
        
        # Create a filter by month option
        months = merged_data["Month"].unique()
        sorted_months = ["Jan", "Feb", "Mar", "April", "May", "June"]
        selected_months = st.multiselect("Select Months", sorted_months, default=sorted_months)
        
        # Filter data based on selected months
        filtered_data = segment_category_data[segment_category_data["Month"].isin(selected_months)]
        
        # Calculate total spend per brand for the selected segment and category
        brand_spending = filtered_data.groupby("Item Brand")["Sales_Amount"].sum().reset_index()
        
        # Calculate total quantity sold per brand for the selected segment and category
        brand_quantity = filtered_data.groupby("Item Brand")["Sold_Quantity"].sum().reset_index()
        
        # Merge total spend and total quantity data
        brand_analysis = pd.merge(brand_spending, brand_quantity, on="Item Brand", how="inner")
        
        # Sort brands by total spend in descending order
        brand_analysis = brand_analysis.sort_values(by="Sales_Amount", ascending=False)
        
        # Display the top N brands
        num_brands_to_display = st.slider("Select Number of Brands:", 1, len(brand_analysis), len(brand_analysis))
        top_brands = brand_analysis.head(num_brands_to_display)
        
        # Split the layout into two columns
        col1, col2 = st.columns([1.2,1])
        
        # Column 1: Display the bar chart
        with col1:
            with st.container():

                # Create a bar chart for brand spending
                fig_brand_analysis = px.bar(
                    top_brands,
                    x="Sales_Amount",
                    y="Item Brand",
                    text="Sales_Amount",  # Add total sales amount as text on bars
                    custom_data=["Sold_Quantity"],  # Store total sales quantity as custom data
                    orientation="h",  # Horizontal bar chart
                    labels={"Sales_Amount": "Total Sales Amount", "Item Brand": "Brand"},
                    title=f"Top {num_brands_to_display} Brands by Total Sales Amount for {selected_segment} Segment"
                )
                
                # Customize the appearance and height
                fig_brand_analysis.update_traces(marker_line_width=1.5, opacity=0.7)
                fig_brand_analysis.update_layout(height=700)  # Adjust the height as needed
                
                # Display the bar chart with total sales amount and quantity numbers
                st.plotly_chart(fig_brand_analysis, use_container_width=True)
        
        # Column 2: Display the pie chart
        with col2:
            # Create a pie chart for brand distribution by units sold
            fig_brand_pie = px.pie(
                top_brands,
                names="Item Brand",
                values="Sold_Quantity",
                labels={"Item Brand": "Brand", "Sold_Quantity": "Units Sold"},
                title=f"Top {num_brands_to_display} Brands Distribution by Units Sold for {selected_segment} Segment"
            )
            
            # Customize the appearance and height
            fig_brand_pie.update_traces(textinfo="percent+label", textposition="inside", pull=[0.2] * num_brands_to_display)
            fig_brand_pie.update_layout(showlegend=False,height=800) 
            
            # Display the pie chart
            st.plotly_chart(fig_brand_pie, use_container_width=True)

        # Display total sales amount and quantity for the selected months and segment
        total_sales = filtered_data["Sales_Amount"].sum()
        total_quantity = filtered_data["Sold_Quantity"].sum()
        st.write(f"<p style='font-size: 22px;'>Total <strong>Sales Amount</strong> for {', '.join(selected_months)} in {selected_segment} Segment: <strong>{total_sales:.2f}</strong></p>", unsafe_allow_html=True)
        st.write(f"<p style='font-size: 22px;'>Total <strong>Quantity Sold</strong> for {', '.join(selected_months)} in {selected_segment} Segment: <strong>{total_quantity:.2f}</strong></p>", unsafe_allow_html=True)

#############################################################################################################################

    elif selected_tab == "Recommendations":
        st.write("go fuck yourselves")

#############################################################################################################################

def retail_main():
    # Add tabs to the app
    tabs = ["Home", "Raw Data", "Customer Segment Distribution", "Average Spend by Segment","Brand Analysis","Recommendations"]
    selected_tab = st.sidebar.selectbox("Select a tab:", tabs)

    if selected_tab == "Home":
        # Display title and description on the home tab
        st.image("Banner.jpg")#, width=1000, use_column_width=False
        st.subheader('''SAKA is a market-driven company that markets and distributes an extensive portfolio of *tires*, *batteries*, *lubricants*, *garage equipment* & *accessories* with offices in Europe, Middle East and Africa. They cater to 300+ tire service centers, fleets & companies in Lebanon.In addition, our offshore operations entail business with subsidiaries and sister companies in several African and MENA countries.''')


    elif selected_tab == "Raw Data":
        # Display the raw data table only
        st.subheader("Raw Data")
        st.write(retail_data)  # Display the DataFrame as a table

#33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

    elif selected_tab == "Customer Segment Distribution":
    
        unique_customers = retail_data.drop_duplicates(subset=["Name", "Segment"])
        # Split the layout into two columns
        col1, col2 = st.columns(2)

        # Column 1: Display the bar graph
        with col1:
            st.subheader("Customer Segment Distribution")
            plot_container = st.container()
            with plot_container:
                st.plotly_chart(plot_segment_distribution(grouped_data_r), use_container_width=False, width=700)

        st.subheader("Find Customer Segment")
        customer_name = st.text_input("Enter Customer Name:")
        if customer_name:
            matching_data = grouped_data_r.loc[grouped_data_r["Name"].str.contains(customer_name, case=False)]
            if not matching_data.empty:
                selected_segment = matching_data["Segment"].iloc[0]
                total_sales = matching_data["Sales_Amount"].iloc[0]
                frequency = matching_data["Frequency"].iloc[0]  # Since there's only one row per customer in grouped_data_r

                st.write(f"Segment: {selected_segment}")
                st.write(f"Total Sales: {total_sales:.2f}")
                st.write(f"Frequency: {frequency}")
            else:
                st.write("Customer not found.")

        
        # Column 2: Show unique customers in each segment
        with col2:
            st.subheader("Unique Customers in Each Segment")
            
            # Calculate unique customers in each segment
            unique_customers = retail_data.drop_duplicates(subset=["Name", "Segment"])
            
            # Order select box options from low to high
            ordered_segments = unique_customers["Segment"].sort_values(ascending=True).unique()
            selected_segment = st.selectbox("Select a Segment:", ordered_segments)
            
            # Display segment and list of unique customers in a DataFrame
            # st.write(f"Segment: {selected_segment}")
            st.write("Customers:")
            
            # Filter and display unique customers for the selected segment
            segment_customers = unique_customers[unique_customers["Segment"] == selected_segment]
            st.dataframe(segment_customers, width=800)

#44444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444

    elif selected_tab == "Average Spend by Segment":
        
        # Split the layout into two columns
        col1, col2 = st.columns(2)
        segment_order = ["Low-Value", "Medium-Value", "High-Value"]
        # Column 1: Spending Pattern Visualization
        with col1:
            st.subheader("Average Spend by Segment")
        
            # Create a radio button to toggle between viewing by individual months and viewing over all months
            view_option = st.radio("View Option", ["All Months","Individual Months"])
        
            if view_option == "Individual Months":
                
                months = retail_data["Month"].unique()
                sorted_months = ["Jan", "Feb", "Mar", "April", "May", "June"]
                selected_months = st.multiselect("Select Months", sorted_months, default=sorted_months)

                # Convert the "Month" column to a categorical data type with custom ordering
                month_order = pd.CategoricalDtype(categories=sorted_months, ordered=True)
                filtered_data = retail_data[retail_data["Month"].isin(selected_months)]
                filtered_data["Month"] = filtered_data["Month"].astype(month_order)

                # Filter data based on selected months
                filtered_data = retail_data[retail_data["Month"].isin(selected_months)]

                # Calculate average spend per segment and month
                avg_spend_per_segment_month = filtered_data.groupby(["Segment", "Month"]).apply(
                    lambda group: group["Sales_Amount"].sum() / group["Name"].nunique()
                ).reset_index(name="Average_Spend")

                # Define the order of segments for the x-axis
                segment_order = ["Low-Value", "Medium-Value", "High-Value"]

                # Create a bar chart using Plotly Express
                # Create a bar chart using Plotly Express
                fig_avg_spend_month = px.bar(
                    avg_spend_per_segment_month,
                    x="Segment",
                    y="Average_Spend",
                    color="Month",
                    barmode="group",  # Use "group" mode for grouped bars
                    category_orders={"Segment": segment_order, "Month": sorted_months},  # Set the category order
                    labels={"Segment": "Segment", "Average_Spend": "Average Spend ($)", "Month": "Month"},
                    title="Average Spend by Segment per Month"
                )

                # Customize the appearance
                fig_avg_spend_month.update_traces(marker_line_width=1.5, opacity=0.7)
                fig_avg_spend_month.update_layout(xaxis_title="Segment", yaxis_title="Average Spend ($)", height=600)

                # Display the bar chart
                st.plotly_chart(fig_avg_spend_month, use_container_width=True)
            else:

                avg_spend_per_segment = retail_data.groupby("Segment").apply(
                    lambda group: group["Sales_Amount"].sum() / group["Name"].nunique()
                ).reset_index(name="Average_Spend")
                
                # Create a bar chart using Plotly Express
                fig_avg_spend = px.bar(
                    avg_spend_per_segment,
                    x="Segment",
                    y="Average_Spend",
                    color="Segment",
                    category_orders={"Segment": segment_order},  # Set the category order
                    labels={"Segment": "Segment", "Average_Spend": "Average Spend"},
                    title="Average Spend by Segment Over Q1 & Q2"
                )
                
                # Customize the appearance
                fig_avg_spend.update_traces(marker_line_width=1.5, opacity=0.7)
                fig_avg_spend.update_layout(xaxis_title="Segment", yaxis_title="Average Spend",height=600)
                
                # Display the bar chart
                st.plotly_chart(fig_avg_spend, use_container_width=True)

        # Column 2: Top Customers by Segment
        with col2:
            st.subheader("Top Customers by Segment")
            
            # Calculate total spending per customer and segment
            total_spending_per_customer = retail_data.groupby(["Segment", "Name"])["Sales_Amount"].sum().reset_index()
            
            # Get the top customers by segment based on total spending
            top_customers_per_segment = total_spending_per_customer.groupby("Segment").apply(
                lambda group: group.nlargest(10, "Sales_Amount")
            ).reset_index(drop=True)
            
            # Create a filter to select the number of customers to display
            num_customers = st.number_input("Select Number of Customers to Display:", min_value=1, max_value=len(top_customers_per_segment),value=5)
            
            # Limit the number of customers based on the filter selection
            top_customers_filtered = top_customers_per_segment.groupby("Segment").head(num_customers)
            
            # Create a bar chart to visualize top customers by segment
            fig_top_customers = px.bar(
                top_customers_filtered,
                x="Name",
                y="Sales_Amount",
                color="Segment",
                category_orders={"Segment": segment_order},  # Set the category order
                labels={"Name": "Customer Name", "Sales_Amount": "Total Spending"},
                title=f"Top {num_customers} Customers by Segment"
            )
            
            # Customize the appearance
            fig_top_customers.update_traces(marker_line_width=1.5, opacity=0.7)
            fig_top_customers.update_layout(xaxis_title="Customer Name", yaxis_title="Total Spending ($)", height=600)
            
            # Display the bar chart
            st.plotly_chart(fig_top_customers, use_container_width=True)
    
#5555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555

    elif selected_tab == "Brand Analysis":
        segment_order = ["Low-Value", "Medium-Value", "High-Value"]
        st.subheader("Brand Analysis")
        
        # Create a filter for selecting a specific segment
        selected_segment = st.selectbox("Select a Segment:", segment_order)
        
        # Create a filter for selecting an item category
        item_categories = retail_data["Item Category"].unique()
        selected_category = st.selectbox("Select an Item Category:", item_categories)
        
        # Filter data based on selected segment and category
        segment_category_data = retail_data[(retail_data["Segment"] == selected_segment) & (retail_data["Item Category"] == selected_category)]
        
        # Create a filter by month option
        months = retail_data["Month"].unique()
        sorted_months = ["Jan", "Feb", "Mar", "April", "May", "June"]
        selected_months = st.multiselect("Select Months", sorted_months, default=sorted_months)
        
        # Filter data based on selected months
        filtered_data = segment_category_data[segment_category_data["Month"].isin(selected_months)]
        
        # Calculate total spend per brand for the selected segment and category
        brand_spending = filtered_data.groupby("Item Brand")["Sales_Amount"].sum().reset_index()
        
        # Calculate total quantity sold per brand for the selected segment and category
        brand_quantity = filtered_data.groupby("Item Brand")["Sold_Quantity"].sum().reset_index()
        
        # Merge total spend and total quantity data
        brand_analysis = pd.merge(brand_spending, brand_quantity, on="Item Brand", how="inner")
        
        # Sort brands by total spend in descending order
        brand_analysis = brand_analysis.sort_values(by="Sales_Amount", ascending=False)
        
        # Display the top N brands
        num_brands_to_display = st.slider("Select Number of Brands:", 1, len(brand_analysis), len(brand_analysis))
        top_brands = brand_analysis.head(num_brands_to_display)
        
        # Split the layout into two columns
        col1, col2 = st.columns([1.2,1])
        
        # Column 1: Display the bar chart
        with col1:
            with st.container():
         
            # Create a bar chart for brand spending
                fig_brand_analysis = px.bar(
                    top_brands,
                    x="Sales_Amount",
                    y="Item Brand",
                    text="Sales_Amount",  # Add total sales amount as text on bars
                    custom_data=["Sold_Quantity"],  # Store total sales quantity as custom data
                    orientation="h",  # Horizontal bar chart
                    labels={"Sales_Amount": "Total Sales Amount", "Item Brand": "Brand"},
                    title=f"Top {num_brands_to_display} Brands by Total Sales Amount for {selected_segment} Segment and {selected_category} Category"
                )
                
                # Customize the appearance and height
                fig_brand_analysis.update_traces(marker_line_width=1.5, opacity=0.7)
                fig_brand_analysis.update_layout(height=750)  # Adjust the height as needed
                
                # Display the bar chart with total sales amount and quantity numbers
                st.plotly_chart(fig_brand_analysis, use_container_width=True)
        
        # Column 2: Display the pie chart
        with col2:
            # Create a pie chart for brand distribution by units sold
            fig_brand_pie = px.pie(
                top_brands,
                names="Item Brand",
                values="Sold_Quantity",
                labels={"Item Brand": "Brand", "Sold_Quantity": "Units Sold"},
                title=f"Top {num_brands_to_display} Brands Distribution by Units Sold for {selected_segment} Segment and {selected_category} Category"
            )
            
            # Customize the appearance and height
            fig_brand_pie.update_traces(textinfo="percent+label", textposition="inside", pull=[0.2] * num_brands_to_display)
            fig_brand_pie.update_layout(showlegend=False,height=800) 
            
            # Display the pie chart
            st.plotly_chart(fig_brand_pie, use_container_width=True)

        # Display total sales amount and quantity for the selected months, segment, and category
        total_sales = filtered_data["Sales_Amount"].sum()
        total_quantity = filtered_data["Sold_Quantity"].sum()
        st.write(f"<p style='font-size: 22px;'>Total <strong>Sales Amount</strong> for {', '.join(selected_months)} in {selected_segment} Segment and {selected_category} Category: <strong>{total_sales:.2f}</strong></p>", unsafe_allow_html=True)
        st.write(f"<p style='font-size: 22px;'>Total <strong>Quantity Sold</strong> for {', '.join(selected_months)} in {selected_segment} Segment and {selected_category} Category: <strong>{total_quantity:.2f}</strong></p>", unsafe_allow_html=True)
    #############################################################################################################################

    elif selected_tab == "Recommendations":
        st.write("""Segment

**High-Value:** All metrics for this category are the highest. Customers belonging to this segment represent loyal customers, and strategies should focus on further enhancing their purchase satisfaction, loyalty, and experience.

**Medium-Value:** Strategically, the "Medium-Value" segment can be cost-effective to engage with. The goal is to further boost their engagement and monetary contribution (Retail & Wholesale). This can be achieved by Targeted Strategies.

o Targeted messages at studied intervals of maintenance & checkups (Retail - Round1).\n
o Offering subsidies or items from poorly performing categories at discounts as complementary promotions to their original purchase categories (Wholesale).\n
o Award frequent customers with promotions (ex. 1 free maintenance check every 3 visits).\n

This could be affective specially with retail customers as around 10800 maintenance and tire services were performed during Q1&Q2.

**Low – Value:** These customers represent a low risk profile. They have brought limited profit to the company and can be utilized by encouraging them to refer new customers to SAKA in return for a discount on a certain service or purchase.
""")

#############################################################################################################################

selected_app = st.sidebar.selectbox("Select App", ("Retail", "Wholesale"))

# Display the selected app based on the choice
if selected_app == "Retail":
    retail_main()
    # st.write("T")
elif selected_app == "Wholesale":
    main()

#############################################################################################################################


st.write("-----")
# Add footer or additional information
st.write('Designed by **Rami Haidar**')

