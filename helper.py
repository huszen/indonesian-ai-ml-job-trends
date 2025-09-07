import numpy as np 
import pandas as pd 
import re 
from datetime import datetime


def clean_salary(s):
    if not isinstance(s, str) or s.strip() == "-" or pd.isna(s):
        return np.nan
    
    s = s.lower()
    s = s.replace("â€“", "-")  # normalize dash
    s = s.replace("rp", "").replace(" ", "")
    
    # detect time unit
    unit = "monthly"
    if "hour" in s or "jam" in s:
        unit = "hourly"
    elif "bulan" in s:
        unit = "monthly"
    
    # remove unit words
    s = re.sub(r"(per.?jam|/hour|bulan|/bulan|/m|/)", "", s)
    
    # normalize decimal separator
    s = s.replace(",", ".")
    
    # keep only valid number parts (digits, dot, k, m, ribu, dash)
    s = re.sub(r"[^0-9\.\-kmribu]", "", s)
    
    # --- Parse values with multipliers ---
    def parse_value(val):
        if "k" in val:
            return float(val.replace("k", "")) * 1_000
        elif "m" in val:
            return float(val.replace("m", "")) * 1_000_000
        elif "ribu" in val:
            return float(val.replace("ribu", "")) * 1_000
        else:
            return float(val)
    
    # split by dash for ranges
    parts = re.split(r"[-–]", s)
    nums = [p for p in parts if p.strip() != ""]
    
    if not nums:
        return np.nan
    
    try:
        parsed = [parse_value(n) for n in nums]
    except ValueError:
        return np.nan  # skip weird cases
    
    if len(parsed) == 1:
        return {"min": parsed[0], "max": parsed[0], "unit": unit}
    else:
        return {"min": min(parsed), "max": max(parsed), "unit": unit}

def map_position(x):
    s = str(x).lower()

    if "ai" in s:
        return "AI Engineer"
    elif "ml" in s or "machine learning" in s:
        return "ML Engineer"
    return "others"

def clean_upload(x):
    if pd.isna(x):
        return np.nan
    
    s = str(x).strip().lower()
    
    # remove dash, parentheses
    s = re.sub(r"[-()]", "", s).strip()
    
    # handle "this day"
    if "this day" in s:
        return 0
    
    # try parse absolute date (e.g., 30-Agu-2025)
    dt = pd.to_datetime(s, format="%d-%b-%Y", errors="coerce")
    if not pd.isna(dt):
        return (datetime.now() - dt).days
    
    # normalize spelling
    s = s.replace("moths", "months")
    s = s.replace("weeks", "week")
    s = s.replace("days", "day")
    s = s.replace("months", "month")
    
    # extract number + unit
    match = re.match(r"(\d+)\s*(day|week|month)", s)
    if not match:
        return np.nan
    
    num, unit = int(match.group(1)), match.group(2)
    
    if unit == "day":
        return num
    elif unit == "week":
        return num * 7
    elif unit == "month":
        return num * 30
    return np.nan

def clean_enthusiast(x):
    if isinstance(x, str) and ">100" in x:
        return 100
    try:
        return int(x)
    except:
        return pd.NA

def clean_degree(x):
    if pd.isna(x) or x.strip == "-":
        return pd.NA

    s = x.strip().lower()
    s = s.replace("â€™", "'")

    if "diploma" in s:
        return "Diploma"
    elif "bachelor" in s and "master" in s:
        return "Bachelor or Master"
    elif "bachelor" in s:
        return "Bachelor"
    elif "master" in s and "phd" in s:
        return "Master or PhD"
    elif "phd" in s:
        return "PhD"
    elif "master" in s:
        return "Master"
    else:
        return pd.NA
    
def clean_location(x):
    s = str(x).lower()
    if "jakarta" in s or "dki" in s:
        return "Jakarta"
    elif "jawa barat" in s:
        return "Jawa Barat"
    elif "banten" in s or "tangerang" in s:
        return "Banten"
    elif "surabaya" in s:
        return "Jawa Timur"
    elif "diy" in s or "yogyakarta" in s:
        return "DIY"
    elif "indonesia" in s:  # generic "Indonesia" without province
        return "Indonesia (unspecified)"
    else:
        return "Others"
    
def normalize_salary(row, work_hours=173, work_days=22):
    """Normalize min/max salary to monthly equivalent."""
    if not isinstance(row, dict):
        return pd.Series([np.nan, np.nan])  # Negotiable or invalid

    min_val, max_val, unit = row["min"], row["max"], row["unit"]

    if unit == "hourly":
        return pd.Series([min_val * work_hours, max_val * work_hours])
    elif unit == "daily":
        return pd.Series([min_val * work_days, max_val * work_days])
    elif unit == "monthly":
        return pd.Series([min_val, max_val])
    else:
        return pd.Series([np.nan, np.nan])




def clean_experience(val):
    if pd.isna(val):
        return "Unspecified"
    
    s = str(val).strip().lower()
    
    # normalize fresh graduate
    if "fresh" in s or "<1" in s or "0" in s:
        return "Fresh Graduate"
    
    # if it's numeric, keep it as "X years"
    try:
        num = float(s)
        if num < 1:
            return "Fresh Graduate"
        else:
            return f"{int(num)} years"
    except:
        return s  # keep original if cannot parse

def normalize_category(x):
    if not isinstance(x, str):
        return "Unspecified"

    s = x.strip().lower()

    # rules
    if "full" in s and "time" in s:
        return "Full-Time"
    elif "part" in s and "time" in s:
        return "Part-time"
    elif "contract" in s:
        return "Contract"
    elif "intern" in s:
        return "Intern"
    elif "freelance" in s:
        return "Freelance"
    elif "unspecified" in s:
        return "Unspecified"
    else:
        return "Other"

def clean_type(x):
    if not isinstance(x, str):
        return "Unspecified"

    s = x.strip().lower()

    if "wfo" in s:
        return "WFO"
    elif "wfh" in s:
        return "WFH"
    elif "hy" in s:
        return "Hybrid"
    else:
        return "Unspecified"


def clean_job_data(df, source_name):
    # Drop columns
    df = df.drop(0)
    df = df.drop(columns=["No","Information","Access Date"], axis=1 )

    # Rename columns
    df = df.rename(columns = {
        "Location ": "Location",
        "WFH/ WFO/ Hybird": "type",
        "length of work experience required (years)": "min_experience",
        "Unnamed: 6": "max_experience",
        "Upload By Company": "days_upload"
    })

    # Apply cleaning and transformation
    df = df.assign(
        Salary=df["Salary"].apply(clean_salary).fillna("Negotiable"),
        days_upload = df["days_upload"].apply(clean_upload).astype("Int64").fillna(-1),
        general_position = df["Position"].apply(map_position),
        Enthusiast = df["Enthusiast"].apply(clean_enthusiast).fillna("Unknown"),
        Degree = df["Degree"].apply(clean_degree).fillna("Unspesicified"),
        Location = df["Location"].apply(clean_location),
        type = df["type"].apply(clean_type),
        min_experience = df["min_experience"].apply(clean_experience),
        source = source_name,
        normalize_category = df["Category"].apply(normalize_category)
    )

    # Extract normalized salary
    df[["min_salary","max_salary"]] = df["Salary"].apply(normalize_salary)

    # Fill salary defaults
    df["min_salary"] = df["min_salary"].fillna("Negotiable")
    df["max_salary"] = df["max_salary"].fillna("Unspesicied")

    # Fill Na
    df['min_experience'] = df['min_experience'].fillna("Unspecified")
    df['max_experience'] = df['max_experience'].fillna("Unspecified")
    df['Category'] = df["Category"].fillna("Unspecified")
    return df