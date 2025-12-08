# import pandas as pd

# def to_seconds(t):
#     h, m = map(int, t.split(":"))
#     return h*3600 + m*60

# def from_seconds(sec):
#     return f"{sec//3600:02d}:{(sec%3600)//60:02d}"

# SHIFT_START = to_seconds("06:00")
# SHIFT_END   = to_seconds("14:00")
# IN_CUTOFF   = to_seconds("05:45")
# OUT_CUTOFF  = to_seconds("14:15")

# def modify_in(punch):
#     sec = to_seconds(punch)
#     return punch if sec >= IN_CUTOFF else from_seconds(SHIFT_START)

# def modify_out(punch):
#     sec = to_seconds(punch)
#     return from_seconds(SHIFT_END) if sec >= OUT_CUTOFF else punch

# def process_excel(path):
#     df = pd.read_excel(path)

#     df["IN_Modified"] = df["In time"].apply(modify_in)
#     df["OUT_Modified"] = df["Out time"].apply(modify_out)

#     return df













import pandas as pd






def process_excel(path):
    df = pd.read_excel(path)

# Combine into full datetime
    df["Shift_In_DateTime"] = df.apply(lambda row: pd.Timestamp.combine(row["Date"], row["In time"]),axis=1)

    df["Shift_Out_DateTime"] = df.apply(lambda row: pd.Timestamp.combine(row["Date"], row["Out time"]),axis=1)



# Convert to datetime
    df["shift_in"] = pd.to_datetime(df["Shift_In_DateTime"])
    df["shift_out"] = pd.to_datetime(df["Shift_Out_DateTime"])

# Define official shift start and end
    official_start = pd.to_datetime("2024-02-01 05:45:00")
    official_end   = pd.to_datetime("2024-02-01 14:15:00")


# Trim logic
    df["shift_in_modified"] = df["Shift_In_DateTime"].apply(lambda x: max(x, official_start))
    df["shift_out_modified"] = df["Shift_Out_DateTime"].apply(lambda x: min(x, official_end))

    print(df.columns.tolist())

    df_modified = df[["Date", "Name ", "Shift", "In time", "Out time", "shift_in_modified", "shift_out_modified"]]

    return df_modified
