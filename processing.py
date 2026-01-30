import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from collections import defaultdict




@dataclass
class EmployeeRTF:
    emp_code: str
    name: str
    date: str
    month: str
    department: str
    shifts: List[Optional[str]] = field(default_factory=list)
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

    


    df_modified = df[["Emp_Code", "Name", "Date", "Shift Start Time", "Shift End Time", "In Time", "Out Time", "Hours Worked", "Status", "In_Time_Modified", "Out_Time_Modified", "Hours_Calculated","Hours_Worked_Modified", "Extra_Hours_Worked_Modified", "Extra_Hours_Worked_Modified_HH_MM"]]

    return df_modified




def process_excel_vallam(path):
    df = pd.read_excel(path, header = None)
    header_idx = df.index[df.apply(lambda r: (r == "Att. Date").any(), axis=1)][0]
    df.columns = df.loc[header_idx].fillna("").tolist()


    df["Emp_Code"] = np.nan
    df["Employee Name"] = np.nan
    df["Department"] = np.nan
    current_emp_code = None
    current_emp_name = None
    current_emp_dept = None



    for i in df.index:
        row = df.loc[i]

    # Detect Emp Department 
        if (row == "Department:").any():
            current_emp_dept = df.iloc[i, 2]

    # Detect Emp_Code row
        if (row == "Emp Code:").any():

            # Extract Emp_Code & name (based on your layout)
            current_emp_code = df.iloc[i, 2]
            current_emp_name = df.iloc[i, 7]   # <-- adjust if name column differs

            continue  # do not assign this row

    # Assign values to all rows until next Emp_Code row
        if current_emp_code is not None:
            df.at[i, "Emp_Code"] = current_emp_code
            df.at[i, "Employee Name"] = current_emp_name
            df.at[i, "Department"] = current_emp_dept



    # Display the DataFrame
    df['Date_DateTime'] = pd.to_datetime(
    df['Att. Date'],
    format='%d-%b-%Y',
    errors='coerce'
)

    # Keep only rows with valid dates
    df = df[df['Date_DateTime'].notna()]



    # 1) Parse columns with explicit formats (avoid the 'could not infer format' warning)
    DATE_FMT = '%d-%b-%Y'   # <-- change if your date is like '12/12/2025' -> '%d/%m/%Y'   
    TIME_FMT = '%H:%M:%S'      # <-- change if your time is like '08:50:30' -> '%H:%M:%S'
    S_TIME_FMT = '%H:%M'

    df['Date_DateTime'] = pd.to_datetime(df['Att. Date'], format=DATE_FMT, errors='coerce')

    # If "In time" is a plain string column like '08:50', you can combine directly:
    df['Shift_In_DateTime'] = pd.to_datetime(
        df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['InTime'],
        format='%d-%m-%Y ' + TIME_FMT,
        errors='coerce'
        )


    df['Shift_Out_DateTime'] = pd.to_datetime(
        df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['OutTime'],
        format='%d-%m-%Y ' + TIME_FMT,
        errors='coerce'
        )

    df['Shift_Start_DateTime'] = pd.to_datetime(
    df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['S. InTime'],
    format='%d-%m-%Y ' + S_TIME_FMT,
    errors='coerce'
    )

    df['Shift_End_DateTime'] = pd.to_datetime(
        df['Date_DateTime'].dt.strftime('%d-%m-%Y') + ' ' + df['S. OutTime'],
        format='%d-%m-%Y ' + S_TIME_FMT,
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

    df["Status"] = df["Status"].str.strip()
    df["Status"] = df["Status"].apply(
    lambda x: "MIS" if isinstance(x, str) and "NO" in x.upper() else x
    )
    df["Status"] = df["Status"].replace({
        "WeeklyOff": "WO",
        "Present": "P",
        "Absent": "A"
    })

    print(df)


    df_modified = df[["Emp_Code", "Employee Name", "Department", "Att. Date", "S. InTime", "S. OutTime", "InTime", "OutTime", "Tot. Dur.", "Status", "Shift", "In_Time_Modified", "Out_Time_Modified", "Hours_Calculated","Hours_Worked_Modified", "Extra_Hours_Worked_Modified", "Extra_Hours_Worked_Modified_HH_MM"]]

    return df_modified








def generate_emp_rtf_from_df(df):

    print("Generating EMP RTF...")
    employees = defaultdict(list)

    last_emp_code = None
    last_month = None

    for _, row in df.iterrows():

        if pd.isna(row["Emp_Code"]):
            continue

        emp_code = row["Emp_Code"]
        date_str = row["Att. Date"]

        try:
            rtf_date = datetime.strptime(date_str.strip(), "%d-%b-%Y")
            rtf_month = rtf_date.month
        except Exception:
            continue  # skip invalid dates

        # Decide if new RTF is needed
        new_rtf_needed = (
            last_emp_code != emp_code or
            last_month != rtf_month
        )

        if new_rtf_needed:
            emp_rtf = EmployeeRTF(
                emp_code=emp_code,
                name=row["Employee Name"],
                date=date_str,
                month=rtf_month,
                department=row["Department"]
            )
            employees[emp_code].append(emp_rtf)

        # Always append to the latest RTF
        current_rtf = employees[emp_code][-1]

        current_rtf.in_times.append(row.get("In_Time_Modified"))
        current_rtf.out_times.append(row.get("Out_Time_Modified"))
        current_rtf.hours_worked.append(row.get("Hours_Worked_Modified"))
        current_rtf.status.append(row.get("Status"))
        current_rtf.extra_hours_worked.append(row.get("Extra_Hours_Worked_Modified"))
        current_rtf.extra_hours_worked_formtd.append(
            row.get("Extra_Hours_Worked_Modified_HH_MM")
        )
        current_rtf.hours_calc.append(row.get("Hours_Calculated"))
        current_rtf.shifts.append(row.get("Shift"))

        last_emp_code = emp_code
        last_month = rtf_month

    #print("EmployeesRTF:", employees)
    return employees





