import streamlit as st
import pandas as pd
import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect("your_database.db")
c = conn.cursor()


def load_data():
    c.execute("SELECT * FROM expenses")
    data = c.fetchall()
    return pd.DataFrame(
        data, columns=["ID", "Date", "Description", "Category", "Amount"]
    )


def update_category(id, new_category):
    c.execute("UPDATE expenses SET category = ? WHERE id = ?", (new_category, id))
    conn.commit()


# Load expenses data
df = load_data()

# Display the dataframe
st.write(df)

# Form to update categories
with st.form(key="edit_category"):
    id_to_edit = st.selectbox("Select expense ID to edit", df["ID"])
    new_category = st.text_input("New category")
    submit_button = st.form_submit_button(label="Update Category")

if submit_button:
    update_category(id_to_edit, new_category)
    st.success("Category updated successfully!")
    # Reload to see changes
    df = load_data()
    st.write(df)
