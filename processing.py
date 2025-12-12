import pandas as pd
import numpy as np






def process_excel(path):
    df = pd.read_excel(path)



    new_header = df.iloc[3] #grab the first row for the header
    df.columns = new_header #set the header row as the df header
    df = df[4:]

    # Display the DataFrame
    print(df)



    # 1) Parse columns with explicit formats (avoid the 'could not infer format' warning)
    DATE_FMT = '%d/%m/%Y'   # <-- change if your date is like '12/12/2025' -> '%d/%m/%Y'
    TIME_FMT = '%H:%M'      # <-- change if your time is like '08:50:30' -> '%H:%M:%S'

    df['Date_DateTime'] = pd.to_datetime(df['Date'], format=DATE_FMT, errors='coerce')

    # If "In time" is a plain string column like '08:50', you can combine directly:
    df['Shift_In_DateTime'] = pd.to_datetime(
        df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['In Time'],
        format='%d-%m-%Y ' + TIME_FMT,
        errors='coerce'
        )


    df['Shift_Out_DateTime'] = pd.to_datetime(
        df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['Out Time'],
        format='%d-%m-%Y ' + TIME_FMT,
        errors='coerce'
        )

    df['Shift_Start_DateTime'] = pd.to_datetime(
    df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['Shift Start Time'],
    format='%d-%m-%Y ' + TIME_FMT,
    errors='coerce'
    )

    df['Shift_End_DateTime'] = pd.to_datetime(
        df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['Shift End Time'],
        format='%d-%m-%Y ' + TIME_FMT,
        errors='coerce'
    )


    df['In_Time_Modified'] = df['Shift_In_DateTime']

    # If Shift_In is earlier than Shift_Start → replace with Shift_Start
    df['In_Time_Modified'] = df['In_Time_Modified'].where(
        df['Shift_In_DateTime'] > df['Shift_Start_DateTime'],
        df['Shift_Start_DateTime']
    )

    # If Shift_In is NaN → force NaN
    df['In_Time_Modified'] = df['In_Time_Modified'].where(
        df['Shift_In_DateTime'].notna(),
        pd.NaT
    )



    df['Out_Time_Modified'] = df['Shift_Out_DateTime']

    # If Shift_In is earlier than Shift_Start → replace with Shift_Start
    df['Out_Time_Modified'] = df['Out_Time_Modified'].where(
        df['Shift_Out_DateTime'] > df['Shift_End_DateTime'],
        df['Shift_End_DateTime']
    )

    # If Shift_In is NaN → force NaN
    df['Out_Time_Modified'] = df['Out_Time_Modified'].where(
        df['Shift_Out_DateTime'].notna(),
        pd.NaT
    )






  



    df['In_Time_Modified'] = df['In_Time_Modified'].dt.strftime('%H:%M')
    df['Out_Time_Modified'] = df['Out_Time_Modified'].dt.strftime('%H:%M')

    df_modified = df[["Paycode", "Name", "Date", "Shift Start Time", "Shift End Time", "In Time", "Out Time", "Hours Worked", "Status", "In_Time_Modified", "Out_Time_Modified"]]

    return df_modified

