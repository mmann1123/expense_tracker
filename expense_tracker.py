# %%
import pandas as pd
from tkinter import filedialog


# create popup window to select multiple files, columns Description, Category, Amount and Date selected regardless of capitalization, and added to a dataframe
def import_files():

    # import filedialog module

    # create a popup window to select multiple files
    file_path = filedialog.askopenfilenames(
        title="Select Files", initialdir="/home/mmann1123/Downloads/"
    )

    # create an empty dataframe
    df = pd.DataFrame()

    # iterate through each file and add to the dataframe
    for file in file_path:
        # read the file into a dataframe
        data = pd.read_csv(
            file,
            usecols=["Description", "Category", "Amount", "Date"],
            dtype={"Description": str, "Category": str, "Amount": float, "Date": str},
        )
        # add the file to the dataframe
        df = pd.concat([df, data], axis=0, ignore_index=True)
    return df


df = import_files()


# create a new cateogry column to group expenses of similar types based on df.Category.unique()


def categorize_expenses(df):
    # create a dictionary of categories
    category = {
        "food": ["groceries", "food"],
        "utilities": ["utilities", "internet", "phone"],
        "housing": [
            "rent",
            "mortgage",
            "home",
            "Lawn & Garden",
        ],
        "transportation": ["gas", "car", "transportation"],
        "entertainment": [
            "entertainment",
            "movies",
            "music",
            "Restaurants",
            "dining",
            "bar",
        ],
        "clothing": ["clothing", "shoes", "apparel"],
        "shopping": ["shopping", "retail", "Sporting Goods"],
        "gifts": ["gifts", "donation", "charity"],
        "health": ["health", "doctor", "pharmacy"],
        "insurance": ["insurance", "premiums"],
        "education": ["education", "school", "books"],
        "other": ["other"],
        "transfer": ["transfer"],
        "income": ["income", "Reimbursement", "Paycheck"],
    }

    # iterate through each category and assign the category to the expense
    for key, value in category.items():
        for item in value:
            df.loc[df["Category"].str.contains(item, case=False), "Category"] = key
    return df


df = categorize_expenses(df)
# %% use streamlit to create a dashboard to show pie chart of expenses by category by month
import streamlit as st
import plotly.express as px


# Function to create dashboard
def dashboard(df):
    # Convert the Date column to a datetime object
    df["Date"] = pd.to_datetime(df["Date"])

    # Create a new column for the month
    df["Month"] = df["Date"].dt.strftime("%Y-%m")

    # Get unique months
    unique_months = df["Month"].unique()

    # Selectbox to choose month
    selected_month = st.selectbox("Select Month", unique_months)

    # Filter dataframe based on selected month
    filtered_df = df[df["Month"] == selected_month]

    # create column of whether this is expense or income based on + or - of Amount
    filtered_df["Type"] = "Expense"
    filtered_df.loc[filtered_df["Amount"] > 0, "Type"] = "Income"

    # Selectbox to choose month
    selected_type = st.selectbox("Select Income or Expense", ["Expense", "Income"])
    # Filter dataframe based on selected month
    filtered_df = filtered_df[filtered_df["Type"] == selected_type]

    # update amounts
    filtered_df["Amount"] = abs(filtered_df["Amount"])

    # Create a pivot table to group the expenses by category
    pivot = filtered_df.pivot_table(
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


# Create dashboard
dashboard(df)


# %%  !streamlit run expense_tracker.py

# %%
