# %%
import pandas as pd
from dateutil import parser
import sqlite3
import streamlit as st
import plotly.express as px


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


# Create dashboard
# dashboard(df)
# Run main app
if __name__ == "__main__":
    main()


# To run this app run:
# # %% !streamlit run expense_tracker.py

# %%
