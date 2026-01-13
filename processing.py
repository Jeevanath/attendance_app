import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional




@dataclass
class EmployeeRTF:
    paycode: str
    name: str
    date: str
    in_times: List[Optional[str]] = field(default_factory=list)
    out_times: List[Optional[str]] = field(default_factory=list)
    hours_worked: List[Optional[str]] = field(default_factory=list)
    hours_calc: List[Optional[float]] = field(default_factory=list)
    status: List[Optional[str]] = field(default_factory=list)
    extra_hours_worked: List[Optional[int]] = field(default_factory=list)
    extra_hours_worked_formtd: List[Optional[int]] = field(default_factory=list)



def hours_to_hhmm(hours):
    if pd.isna(hours):
        return ""

    total_minutes = int(round(hours * 60))
    hh = total_minutes // 60
    mm = total_minutes % 60

    return f"{hh:02d}:{mm:02d}"




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


  #  df['In_Time_Modified'] = df['Shift_In_DateTime']

    # If Shift_In is earlier than Shift_Start → replace with Shift_Start
  #  df['In_Time_Modified'] = df['In_Time_Modified'].where(
       # df['Shift_In_DateTime'] > df['Shift_Start_DateTime']- pd.Timedelta(minutes=15),
     #   df['Shift_Start_DateTime']
   # )

    mask = df['Shift_In_DateTime'] < (df['Shift_Start_DateTime'] - pd.Timedelta(minutes=15))

    minute_offsets = np.random.randint(-15, 16, size=len(df))
    random_deltas = pd.to_timedelta(minute_offsets, unit='m')
    random_times_all = df['Shift_Start_DateTime'] + random_deltas

    df['In_Time_Modified'] = df['Shift_In_DateTime'].where(~mask, random_times_all)




    # If Shift_In is NaN → force NaN
    df['In_Time_Modified'] = df['In_Time_Modified'].where(
        df['Shift_In_DateTime'].notna(),
        pd.NaT
    )


    








    



   # df['Out_Time_Modified'] = df['Shift_Out_DateTime']

    # If Shift_In is earlier than Shift_Start → replace with Shift_Start
   # df['Out_Time_Modified'] = df['Out_Time_Modified'].where(
      #  df['Shift_Out_DateTime'] < df['Shift_End_DateTime']+ pd.Timedelta(minutes=15),
       # df['Shift_End_DateTime']
   # )

    mask = df['Shift_Out_DateTime'] > (df['Shift_End_DateTime'] + pd.Timedelta(minutes=15))

    minute_offsets = np.random.randint(-15, 16, size=len(df))
    random_deltas = pd.to_timedelta(minute_offsets, unit='m')
    random_times_all = df['Shift_End_DateTime'] + random_deltas

    df['Out_Time_Modified'] = df['Shift_Out_DateTime'].where(~mask, random_times_all)

    # If Shift_Out is NaN → force NaN
    df['Out_Time_Modified'] = df['Out_Time_Modified'].where(
        df['Shift_Out_DateTime'].notna(),
        pd.NaT
    )





    # Handle overnight shifts (Out < In → add 1 day)
    overnight_mask = df['Out_Time_Modified'] < df['In_Time_Modified']
    df.loc[overnight_mask, 'Out_Time_Modified'] += pd.Timedelta(days=1)

    # Calculate duration
    df['Hours_Calculated'] = (
        df['Out_Time_Modified'] - df['In_Time_Modified']
    ).dt.total_seconds() / 3600

    df['Hours_Calculated'] = df['Hours_Calculated'].where(
        df['In_Time_Modified'].notna() & df['Out_Time_Modified'].notna(),
        np.nan
    )
    df['Hours_Calculated'] = df['Hours_Calculated'].round(2)



  



    df['In_Time_Modified'] = df['In_Time_Modified'].dt.strftime('%H:%M')
    df['Out_Time_Modified'] = df['Out_Time_Modified'].dt.strftime('%H:%M')
    df.loc[df['Hours_Calculated'] < 6, 'Status'] = 'H'



    df['Extra_Hours_Worked_Modified'] = (
                                            df['Hours_Calculated'] - 8.5
                                            ).where(df['Hours_Calculated'] > 8.5, 0)
    df['Hours_Worked_Modified'] = df['Hours_Calculated'].apply(hours_to_hhmm)
    df['Extra_Hours_Worked_Modified_HH_MM'] = df['Extra_Hours_Worked_Modified'].apply(hours_to_hhmm)

    


    df_modified = df[["Paycode", "Name", "Date", "Shift Start Time", "Shift End Time", "In Time", "Out Time", "Hours Worked", "Status", "In_Time_Modified", "Out_Time_Modified", "Hours_Calculated","Hours_Worked_Modified", "Extra_Hours_Worked_Modified", "Extra_Hours_Worked_Modified_HH_MM"]]

    return df_modified





def generate_emp_rtf_from_df(df):
    employees = {}

    for _, row in df.iterrows():
        if pd.isna(row["Paycode"]):
            continue
        paycode = row["Paycode"]


        if paycode not in employees:
            employees[paycode] = EmployeeRTF(
                paycode=paycode,
                name=row["Name"],
                date=row["Date"]
            )

        employees[paycode].in_times.append(row["In_Time_Modified"])
        employees[paycode].out_times.append(row["Out_Time_Modified"])
        employees[paycode].hours_worked.append(row["Hours_Worked_Modified"])
        employees[paycode].status.append(row["Status"])
        employees[paycode].extra_hours_worked.append(row["Extra_Hours_Worked_Modified"])
        employees[paycode].extra_hours_worked_formtd.append(row["Extra_Hours_Worked_Modified_HH_MM"])
        employees[paycode].hours_calc.append(row["Hours_Calculated"])



    return employees




