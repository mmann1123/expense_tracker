# %% environment expense
import pandas as pd
from dateutil import parser

# create an empty dataframe
df = pd.DataFrame()

for file in [
    "/home/mmann1123/Downloads/chasemike.CSV",
    "/home/mmann1123/Downloads/joint-visa.csv",
    "/home/mmann1123/Downloads/mike visa.csv",
    "/home/mmann1123/Downloads/carlynchase.CSV",
]:
    # read the file into a dataframe
    data = pd.read_csv(
        file
        # usecols=["Description", "Category", "Amount", "Date"],
        # dtype={"Description": str, "Category": str, "Amount": float, "Date": str},
    )

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
    data = data[["Date", "Description", "Category", "Amount"]]
    data["Date"] = data["Date"].apply(lambda x: parser.parse(x))

    # add the file to the dataframe
    df = pd.concat([df, data], axis=0, ignore_index=True)

# %%
