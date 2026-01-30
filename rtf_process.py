
import calendar
from datetime import datetime
import numpy as np
import pandas as pd
from string import Template



def hours_to_hhmm(hours):
    if pd.isna(hours):
        return ""

    total_minutes = int(round(hours * 60))
    hh = total_minutes // 60
    mm = total_minutes % 60

    return f"{hh:02d}:{mm:02d}"




"""def generate_shift_list(date_str, default_shift="G"):

    date_str format: DD/MM/YYYY
    returns list like ['G', '', 'G', 'G', ...]
    Sundays -> ''

    dt = datetime.strptime(date_str, "%d-%b-%Y")
    year, month = dt.year, dt.month

    days_in_month = calendar.monthrange(year, month)[1]

    shifts = []

    for day in range(1, days_in_month + 1):
        current_date = datetime(year, month, day)

        if current_date.weekday() == 6:  # Sunday
            shifts.append("'")
        else:
            shifts.append(default_shift)

    return shifts """





def build_day_header(start_x=1560, y=2471, step=480, days=31):
    """
    Generates the day-number row (01–31) exactly like Crystal Reports
    """
    block = ""

    for day in range(1,days+1):
        day_str = f"{day:02d}"

        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\fi0\qr
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {day_str}}}\par}}
"""
        start_x += step

    return block



def build_day_header2(date_str, start_x=1560, y=2471, step=480):
    """
    Generates the day-number row (01–28/29/30/31)
    date_str format: DD/MM/YYYY
    """

    print("Date :",date_str)
    dt = datetime.strptime(date_str, "%d-%b-%Y")
    days = calendar.monthrange(dt.year, dt.month)[1]

    block = ""

    for day in range(1, days + 1):
        day_str = f"{day:02d}"

        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\fi0\qr
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {day_str}}}\par}}
"""
        start_x += step

    return block



def month_year_from_date(date_str: str) -> str:
    """
    date_str format: DD/MM/YYYY
    returns: 'MONTH YYYY'
    """
    dt = datetime.strptime(date_str, "%d-%b-%Y")
    return dt.strftime("%B %Y").upper()




def build_shift_header(
    shifts,
    start_x=1560,
    y=2902,
    step=480
):
    """
    Builds the Shift row (G / - / A / B etc.)
    aligned exactly under the day header
    """
    block = ""

    for shift in shifts:
        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\qr\vertalt
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {shift}}}\par}}
"""
        start_x += step

    return block




def build_shift_in_header(
    shifts,
    start_x=1560,
    y=3228,
    step=480
):
    """
    Builds the Shift row (G / - / A / B etc.)
    aligned exactly under the day header
    """
    block = ""

    for shift in shifts:
        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\qr\vertalt
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {shift}}}\par}}
"""
        start_x += step

    return block


def build_shift_out_header(
    shifts,
    start_x=1560,
    y=3554,
    step=480
):
    """
    Builds the Shift row (G / - / A / B etc.)
    aligned exactly under the day header
    """
    block = ""

    for shift in shifts:
        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\qr\vertalt
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {shift}}}\par}}
"""
        start_x += step

    return block



def build_atd_header(
    shifts,
    start_x=1560,
    y=3880,
    step=480
):
    """
    Builds the Shift row (G / - / A / B etc.)
    aligned exactly under the day header
    """
    block = ""

    for shift in shifts:
        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\qr\vertalt
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {shift}}}\par}}
"""
        start_x += step

    return block



def build_hrs_worked_header(
    shifts,
    start_x=1560,
    y=4206,
    step=480
):
    """
    Builds the Shift row (G / - / A / B etc.)
    aligned exactly under the day header
    """
    block = ""

    for shift in shifts:
        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\qr\vertalt
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {shift}}}\par}}
"""
        start_x += step

    return block


def build_extra_hrs_worked_header(
    shifts,
    start_x=1560,
    y=4532,
    step=480
):
    """
    Builds the extra hours row 
    aligned exactly under the day header
    """
    block = ""

    for shift in shifts:
        block += rf"""
{{\pard\pvpg\phpg\posx{start_x}\posy{y}\absw360\absh-221\qr\vertalt
{{\f0\b0\i0\ul0\strike0\fs13\cf1 {shift}}}\par}}
"""
        start_x += step

    return block






def generate_rtf(emprtf, tpl, page_num = 1, total_pages=1):
    #with open(REPORT_TEMPLATE, "r", encoding="utf-8") as f:
    #   tpl = Template(f.read())

    if total_pages != 1:
        tpl = Template(tpl)
    #print("TOtal hours list",emprtf.hours_calc )
    THW = np.nansum(emprtf.hours_calc)     #Calculation for TOtal hours worked in hh:mm
    THW = hours_to_hhmm(THW)

    TEHW = np.nansum(emprtf.extra_hours_worked)     #Calculation for Extra hours worked in hh:mm
    TEHW = hours_to_hhmm(TEHW)


    emprtf.in_times = ["'" if x != x else x for x in emprtf.in_times]
    emprtf.out_times = ["'" if x != x else x for x in emprtf.out_times]
    emprtf.hours_worked = ["'" if x != x else x for x in emprtf.hours_worked]
    emprtf.status = ['-' if x == "WO" else x for x in emprtf.status]
    emprtf.status = ['X' if x == "P" else x for x in emprtf.status]
    emprtf.status = ['/' if x == "H" else x for x in emprtf.status]
    emprtf.status = ['OD' if x == "POW" else x for x in emprtf.status]
    emprtf.extra_hours_worked_formtd = ["'" if x == "00:00" else x for x in emprtf.extra_hours_worked_formtd]

    shifts = emprtf.shifts
    shifts_in = emprtf.in_times
    shifts_out = emprtf.out_times
    atd = emprtf.status
    hrs_worked = emprtf.hours_worked
    extra_hrs_worked = emprtf.extra_hours_worked_formtd





    day_header = build_day_header2(date_str = emprtf.date)
    shift_header = build_shift_header(shifts)
    shift_in_header = build_shift_in_header(shifts_in)
    shift_out_header = build_shift_out_header(shifts_out)
    atd_header = build_atd_header(atd)
    hrs_worked_header = build_hrs_worked_header(hrs_worked)
    extra_hrs_worked_header = build_extra_hrs_worked_header(extra_hrs_worked)


    filled_rtf = tpl.substitute(
        DAY_HEADER=day_header,
        SHIFT_HEADER=shift_header,
        SHIFT_IN_HEADER=shift_in_header,
        SHIFT_OUT_HEADER=shift_out_header,
        HRS_WORKED_HEADER=hrs_worked_header,
        EXTRA_HRS_WORKED_HEADER=extra_hrs_worked_header,
        ATD_HEADER=atd_header,
        EMPCODE=emprtf.emp_code,
        NAME=emprtf.name,
        MONTH_YEAR=month_year_from_date(emprtf.date),
        P=page_num,
        TOT_P=total_pages,
        DEPARTMENT=emprtf.department,
        TDP=str(emprtf.status.count("X") + emprtf.status.count("MIS") + emprtf.status.count("/")+ emprtf.status.count("OD")),
        TA=str(emprtf.status.count("A")),
        TDW=str(emprtf.status.count("X") + emprtf.status.count("MIS") + emprtf.status.count("/") + emprtf.status.count("OD")),
        THW=str(THW),
        TEHW=str(TEHW),
        TWO=0,
        TCL=0,
        TCO=0,
        TOD=str(emprtf.status.count("OD")),
        TEL=0,
        TLO=0,
        ML=0
    )

    return filled_rtf

def extract_rtf_header_footer(rtf_text):
    parts = rtf_text.template.split(r'\sectd')
    header = parts[0]
    body = '\sectd' + parts[1]
    body = body[:-1]
    return header, body


def generate_all_employees_rtf(employees: dict, template_text: str) -> str:
    """
    employees: dict[emp_code -> EmployeeRTF]
    template_text: RTF template for ONE employee

    Returns full RTF with 2 employees per page
    """
    header, body = extract_rtf_header_footer(template_text)
    final_rtf = [header]
    emp_list = employees.values()
    total_pages = len(emp_list)
    page_num = 1

    for rtf_list in employees.values():
        for rtf in rtf_list:
            emp_rtf = generate_rtf(rtf, body, page_num, total_pages)
            final_rtf.append(emp_rtf)

        # After every 2 employees, insert page break (except last)
        #if (idx + 1) % 2 == 0 and (idx + 1) < len(emp_list):
            final_rtf.append(r"\page\sect")
            page_num += 1

    
    return "\n".join(final_rtf) + "}"



