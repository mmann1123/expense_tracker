# %%
import pandas as pd
from dateutil import parser


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
        data = data[["Date", "Description", "Category", "Amount"]]
        data["Date"] = data["Date"].apply(lambda x: parser.parse(x, fuzzy=True))

        # add the file to the dataframe
        df = pd.concat([df, data], axis=0, ignore_index=True)
        df.dropna(inplace=True)

    return df


out = import_files(
    [
        "/home/mmann1123/Downloads/joint.csv",
        "/home/mmann1123/Downloads/mike.csv",
        # "/home/mmann1123/Downloads/checkin.csv",
    ]
)
print(out)
# %% environment expense
import pandas as pd
from dateutil import parser

# create an empty dataframe
df = pd.DataFrame()


for file in [
    "/home/mmann1123/Downloads/mike.csv",
    "/home/mmann1123/Downloads/joint.csv",
    # "/home/mmann1123/Downloads/checkin.csv",
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
import pandas as pd

# read the file into a dataframe
df = pd.read_csv("/home/mmann1123/Downloads/checkin.csv")

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
df
# %%
