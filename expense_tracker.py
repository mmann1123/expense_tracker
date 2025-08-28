# %%
import pandas as pd
from dateutil import parser
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Function to remove duplicates and save to SQLite
def process_data(df):
    # Assuming 'Category' and other necessary columns are present
    df = df.drop_duplicates()
    # Connect to SQLite database (or create if not exist)
    conn = sqlite3.connect("expenses.db")
    # Save the dataframe to SQLite table 'expenses'
    df.to_sql("expenses", conn, if_exists="replace", index=False)
    conn.close()


# Function to load data for editing
def load_data():
    conn = sqlite3.connect("expenses.db")
    query = "SELECT * FROM expenses"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def edit_data():
    # Load data
    df = load_data()

    # Assuming you want to allow users to edit 'Category' for now
    category_to_edit = st.selectbox("Select Entry to Edit", df.index)
    new_category = st.text_input(
        "New Category", value=df.loc[category_to_edit, "Category"]
    )

    if st.button("Update"):
        # Update the DataFrame
        df.loc[category_to_edit, "Category"] = new_category

        # Save changes back to the database
        conn = sqlite3.connect("expenses.db")
        df.to_sql("expenses", conn, if_exists="replace", index=False)
        conn.close()
        st.success("Updated Successfully")


# create popup window to select multiple files, columns Description, Category, Amount and Date selected regardless of capitalization, and added to a dataframe
def import_files(files):

    # create an empty dataframe
    df = pd.DataFrame()

    # iterate through each file and add to the dataframe
    for file in files:
        # read the file into a dataframe
        data = pd.read_csv(file)

        # convert the columns to lowercase
        data.columns = data.columns.str.capitalize()
        # check if all ["Description", "Category", "Amount", "Date"] in columns
        if not all(
            col in data.columns for col in ["Description", "Category", "Amount", "Date"]
        ):

            # rename first column to "Date" if it is not already named "Date"
            if "Date" not in data.columns:
                try:
                    data = data.rename(
                        columns={
                            data.filter(
                                like="Date",
                            ).columns[0]: "Date"
                        }
                    )
                except IndexError:
                    data = data.rename(
                        columns={
                            data.filter(
                                like="date",
                            ).columns[0]: "Date"
                        }
                    )
            # select the first column with "Descritpion" in the name and rename it to "Description"
            if "Description" not in data.columns:
                data = data.rename(
                    columns={data.filter(like="Description").columns[0]: "Description"}
                )
        # Remove any row that contains the word "declined" ignoring case
        data = data[
            ~data.apply(
                lambda row: row.astype(str).str.contains("declined", case=False).any(),
                axis=1,
            )
        ]

        data = data[["Date", "Description", "Category", "Amount"]]
        data["Date"] = data["Date"].apply(lambda x: parser.parse(x, fuzzy=True))

        # add the file to the dataframe
        df = pd.concat([df, data], axis=0, ignore_index=True)
        df.dropna(inplace=True)
    return df


# create a new cateogry column to group expenses of similar types based on df.Category.unique()


def categorize_expenses(df):
    # create a dictionary of categories
    category = {
        "Food": ["groceries", "food"],
        "Utilities": ["utilities", "internet", "phone"],
        "Housing": [
            "rent",
            "mortgage",
            "home",
            "Lawn & Garden",
        ],
        "Transportation": ["gas", "car$", "transportation"],
        "Entertainment": [
            "entertainment",
            "movies",
            "music",
            "Restaurant",
            "dining",
            "alcohol",
            "bar",
        ],
        "Travel": ["travel", "hotel", "airfare", "vacation"],
        "Clothing": ["clothing", "shoes", "apparel"],
        "Shopping": ["shopping", "retail", "Sporting Goods"],
        "Gifts": ["gifts", "donation", "charity"],
        "Health": ["health", "doctor", "pharmacy"],
        "Insurance": ["insurance", "premiums"],
        "Education": ["education", "school", "books"],
        "Other": ["other"],
        "Transfer/Payment": ["transfer", "credit card", "payment"],
        "Income": ["income", "reimbursement", "paycheck"],
    }

    # iterate through each category and assign the category to the expense
    for key, value in category.items():
        for item in value:
            df.loc[df["Category"].str.contains(item, case=False), "Category"] = key

    # Convert the Date column to a datetime object
    df["Date"] = pd.to_datetime(df["Date"])

    # Create a new column for the month
    df["Month"] = df["Date"].dt.strftime("%Y-%m")

    # Get unique months
    unique_months = df["Month"].unique()
    return df


# df = categorize_expenses(df)
# %% use streamlit to create a dashboard to show pie chart of expenses by category by month


def main():
    st.set_page_config(page_title="Expense Tracker", layout="wide")
    
    # Title Image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("static/ascii-text-art.png", width=600)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files", accept_multiple_files=True, type=["csv"]
    )
    if uploaded_files:
        df = import_files(uploaded_files)
        df = categorize_expenses(df)
        process_data(df)  # Process and save to database
        df = load_data()  # Load data for editing
        st.session_state.df = df

    # if st.button("Load Data"):
    #     df = load_data()  # Load data for editing
    #     st.write(df)  # Display data

    if "df" in st.session_state:
        df = st.session_state.df
        
        # Create tabs
        tab1, tab2 = st.tabs([ "Trends Analysis","Monthly Dashboard"])
        
        with tab1:
            trends_analysis(df)
        
        with tab2:
            dashboard(df)
    else:
        st.write("Please upload data files.")

    # Optional: Interface to add/edit entries
    # This is a simple form to add or edit expenses. In a real app, you'd likely want more control.
    # if st.button("Edit Data"):
    #     edit_data()


# Function to create dashboard
def dashboard(df):
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Create a new column for the month
    df["Month"] = df["Date"].dt.strftime("%Y-%m")

    # Get unique months
    unique_months = df["Month"].unique()

    # Selectbox to choose month
    selected_month = st.selectbox("Select Month", unique_months)

    # Filter dataframe based on selected month
    month_df = df[df["Month"] == selected_month]

    # create column of whether this is expense or income based on + or - of Amount
    month_df["Type"] = "Expense"
    month_df.loc[month_df["Category"].str.contains("Income", case=False), "Type"] = (
        "Income"
    )
    month_df.loc[
        month_df["Category"].str.contains("Transfer/Payment", case=False), "Type"
    ] = "Transfer"

    # st.write(month_df) display input data
    # Selectbox to choose month
    selected_type = st.selectbox(
        "Select Income or Expense",
        [
            "Expense",
            "Income",
            "Transfer",
        ],
    )
    # Filter dataframe based on selected month
    filtered_df2 = month_df[month_df["Type"] == selected_type]

    # update amounts
    filtered_df2["Amount"] = abs(filtered_df2["Amount"])

    # Create a pivot table to group the expenses by category
    pivot = filtered_df2.pivot_table(
        index="Month", columns="Category", values="Amount", aggfunc="sum"
    ).fillna(0)
    # Reset the index of the pivot table to make "Month" a regular column
    pivot.reset_index(inplace=True)

    # Melt the pivot table to transform it into a long-form DataFrame
    melted_df = pivot.melt(
        id_vars=["Month"], var_name="Category", value_name="Total Amount"
    )

    # Create a pie chart to show the expenses by category
    fig = px.pie(
        melted_df,
        names="Category",
        values="Total Amount",
        hole=0.3,
        color="Category",
        title="Expenses by Category",
        color_discrete_sequence=px.colors.qualitative.Set3,  # Specify a color palette
    )

    # fig.show()
    # Display the pie chart
    st.plotly_chart(fig)

    # display total expenses and total income

    # create column of whether this is expense or income based on + or - of Amount
    total_expense = (
        month_df[
            (month_df["Type"] == "Expense")
            & (~month_df["Category"].str.contains("Transfer/Payment", case=False))
        ]["Amount"]
        .abs()
        .sum()
    )

    total_income = month_df[month_df["Type"] == "Income"]["Amount"].sum()
    st.write(
        f"Total Income: {total_income:,.2f}  Total Expense: {total_expense:,.2f} Net: {(total_income - abs(total_expense)):,.2f}"
    )

    unique_categories = sorted([category for category in month_df["Category"].unique()])

    # Create a table of total values for each unique category
    category_totals = month_df.groupby("Category")["Amount"].sum().reset_index()
    category_totals.columns = ["Category", "Total Amount"]
    st.write("Total Values for Each Category")
    st.write(category_totals)

    # create dropdown to select a category and display a table of expenses for that category
    selected_category = st.selectbox("Select Category", unique_categories)
    # Filter dataframe based on selected category
    filtered_df = month_df[month_df["Category"] == selected_category]
    filtered_df.sort_values("Amount", ascending=True, inplace=True)
    filtered_df["Date"] = filtered_df["Date"].dt.strftime("%Y-%m-%d")
    # Display the table
    st.write(filtered_df)


# Function to create trends analysis
def trends_analysis(df):
    st.title("Expense Trends Over Time")
    
    # Ensure Date column is datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.strftime("%Y-%m")
    
    # Create Type column
    df["Type"] = "Expense"
    df.loc[df["Category"].str.contains("Income", case=False), "Type"] = "Income"
    df.loc[df["Category"].str.contains("Transfer/Payment", case=False), "Type"] = "Transfer"
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "Analysis Type", 
            ["Total Spending", "Category Trends", "Net Cash Flow", "Monthly Breakdown"]
        )
    
    with col2:
        # Date range filter
        min_date = df["Date"].min()
        max_date = df["Date"].max()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Filter data by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & 
                        (df["Date"] <= pd.to_datetime(end_date))]
    else:
        filtered_df = df
    
    if analysis_type == "Total Spending":
        # Total spending trend over time
        monthly_totals = filtered_df[filtered_df["Type"] == "Expense"].groupby("Month")["Amount"].apply(lambda x: x.abs().sum()).reset_index()
        monthly_totals["Month"] = pd.to_datetime(monthly_totals["Month"])
        monthly_totals = monthly_totals.sort_values("Month")
        
        fig = px.line(monthly_totals, x="Month", y="Amount", 
                     title="Total Monthly Spending Trend",
                     markers=True)
        fig.update_layout(xaxis_title="Month", yaxis_title="Total Spending ($)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Monthly Spending", f"${monthly_totals['Amount'].mean():.2f}")
        with col2:
            st.metric("Highest Month", f"${monthly_totals['Amount'].max():.2f}")
        with col3:
            st.metric("Lowest Month", f"${monthly_totals['Amount'].min():.2f}")
        with col4:
            st.metric("Total Period", f"${monthly_totals['Amount'].sum():.2f}")
    
    elif analysis_type == "Category Trends":
        # Category spending trends using predefined categories
        main_categories = [
            "Food", "Utilities", "Housing", "Transportation", "Entertainment", 
            "Travel", "Clothing", "Shopping", "Gifts", "Health", 
            "Insurance", "Education", "Other"
        ]
        
        category_monthly = filtered_df[filtered_df["Type"] == "Expense"].groupby(["Month", "Category"])["Amount"].apply(lambda x: x.abs().sum()).reset_index()
        
        # Filter to only show main categories (exclude Transfer/Payment and Income)
        category_monthly_filtered = category_monthly[category_monthly["Category"].isin(main_categories)]
        
        # Select categories to display
        available_categories = sorted(category_monthly_filtered["Category"].unique())
        selected_categories = st.multiselect(
            "Select Categories to Compare", 
            available_categories, 
            default=available_categories[:5] if len(available_categories) >= 5 else available_categories
        )
        
        if selected_categories:
            category_filtered = category_monthly_filtered[category_monthly_filtered["Category"].isin(selected_categories)]
            category_filtered["Month"] = pd.to_datetime(category_filtered["Month"])
            category_filtered = category_filtered.sort_values("Month")
            
            fig = px.line(category_filtered, x="Month", y="Amount", color="Category",
                         title="Category Spending Trends Over Time",
                         markers=True)
            fig.update_layout(xaxis_title="Month", yaxis_title="Amount ($)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Category comparison table
            st.subheader("Category Totals Comparison")
            category_totals = category_filtered.groupby("Category")["Amount"].sum().sort_values(ascending=False).reset_index()
            st.dataframe(category_totals)
    
    elif analysis_type == "Net Cash Flow":
        # Net cash flow analysis
        monthly_income = filtered_df[filtered_df["Type"] == "Income"].groupby("Month")["Amount"].sum().reset_index()
        monthly_expense = filtered_df[filtered_df["Type"] == "Expense"].groupby("Month")["Amount"].apply(lambda x: x.abs().sum()).reset_index()
        
        # Merge income and expense data
        cash_flow = pd.merge(monthly_income, monthly_expense, on="Month", how="outer", suffixes=("_Income", "_Expense")).fillna(0)
        cash_flow["Net_Flow"] = cash_flow["Amount_Income"] - cash_flow["Amount_Expense"]
        cash_flow["Month"] = pd.to_datetime(cash_flow["Month"])
        cash_flow = cash_flow.sort_values("Month")
        
        # Create subplot with income, expense, and net flow
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=cash_flow["Month"], y=cash_flow["Amount_Income"], 
                      mode="lines+markers", name="Income", line=dict(color="green")),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=cash_flow["Month"], y=cash_flow["Amount_Expense"], 
                      mode="lines+markers", name="Expenses", line=dict(color="red")),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=cash_flow["Month"], y=cash_flow["Net_Flow"], 
                      mode="lines+markers", name="Net Flow", line=dict(color="blue", width=3)),
            secondary_y=False,
        )
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount ($)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cash flow metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_net = cash_flow["Net_Flow"].mean()
            st.metric("Average Monthly Net Flow", f"${avg_net:.2f}", delta=None if avg_net >= 0 else "Deficit")
        with col2:
            total_income = cash_flow["Amount_Income"].sum()
            st.metric("Total Income", f"${total_income:.2f}")
        with col3:
            total_expense = cash_flow["Amount_Expense"].sum()
            st.metric("Total Expenses", f"${total_expense:.2f}")
    
    elif analysis_type == "Monthly Breakdown":
        # Detailed monthly breakdown with multiple visualizations
        st.subheader("Monthly Expense Breakdown")
        
        # Heatmap of spending by category and month
        monthly_category = filtered_df[filtered_df["Type"] == "Expense"].groupby(["Month", "Category"])["Amount"].apply(lambda x: x.abs().sum()).reset_index()
        heatmap_data = monthly_category.pivot(index="Category", columns="Month", values="Amount").fillna(0)
        
        fig = px.imshow(heatmap_data, 
                       title="Spending Heatmap by Category and Month",
                       labels=dict(x="Month", y="Category", color="Amount ($)"),
                       aspect="auto")
        st.plotly_chart(fig, use_container_width=True)
        
        # Top spending months
        st.subheader("Top Spending Months")
        monthly_totals = filtered_df[filtered_df["Type"] == "Expense"].groupby("Month")["Amount"].apply(lambda x: x.abs().sum()).reset_index()
        monthly_totals = monthly_totals.sort_values("Amount", ascending=False).head(10)
        
        fig = px.bar(monthly_totals, x="Month", y="Amount",
                    title="Top 10 Highest Spending Months")
        st.plotly_chart(fig, use_container_width=True)


# Create dashboard
# dashboard(df)
# Run main app
if __name__ == "__main__":
    main()


# To run this app run:
# # %% !streamlit run expense_tracker.py

# %%
