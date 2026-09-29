import pandas as pd
import numpy as np

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate fare observations.
    Dedup on: scrape_date, travel_date, origin, destination, carrier, flight_number
    Keep the first occurrence.
    """
    if df.empty:
        return df
        
    dedup_cols = ["scrape_date", "travel_date", "origin", "destination", "carrier", "flight_number"]
    existing_cols = [col for col in dedup_cols if col in df.columns]
    
    return df.drop_duplicates(subset=existing_cols, keep="first").reset_index(drop=True)

def detect_outliers_iqr(df: pd.DataFrame, column: str = "total_fare", factor: float = 1.5) -> pd.DataFrame:
    """
    Mark outliers using IQR method per route+advance_days group.
    Groups by (origin, destination, advance_days).
    Outliers = values below Q1 - factor*IQR or above Q3 + factor*IQR.
    Sets is_outlier = 1 for outlier rows.
    Preserves all original columns.
    """
    if df.empty or column not in df.columns:
        return df
        
    df = df.copy()
    if "is_outlier" not in df.columns:
        df["is_outlier"] = 0
        
    groups = ["origin", "destination", "advance_days"]
    existing_groups = [g for g in groups if g in df.columns]
    
    if not existing_groups:
        return df
        
    grouped = df.groupby(existing_groups)[column]
    q1 = grouped.transform(lambda x: x.quantile(0.25))
    q3 = grouped.transform(lambda x: x.quantile(0.75))
    count = grouped.transform("count")
    iqr = q3 - q1
    lower_bound = q1 - (factor * iqr)
    upper_bound = q3 + (factor * iqr)
    
    mask = (count >= 4) & ((df[column] < lower_bound) | (df[column] > upper_bound))
    df.loc[mask, "is_outlier"] = 1
    return df

def detect_outliers_zscore(df: pd.DataFrame, column: str = "total_fare", threshold: float = 3.0) -> pd.DataFrame:
    """
    Alternative outlier detection using z-score per route group.
    Preserves all original columns.
    """
    if df.empty or column not in df.columns:
        return df
        
    df = df.copy()
    if "is_outlier" not in df.columns:
        df["is_outlier"] = 0
        
    groups = ["origin", "destination", "advance_days"]
    existing_groups = [g for g in groups if g in df.columns]
    
    if not existing_groups:
        return df
        
    grouped = df.groupby(existing_groups)[column]
    mean = grouped.transform("mean")
    std = grouped.transform("std")
    count = grouped.transform("count")
    
    mask = (count >= 3) & (std > 0) & (np.abs((df[column] - mean) / std) > threshold)
    df.loc[mask, "is_outlier"] = 1
    return df

def handle_missing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing/sold-out flights.
    - Don't drop SOLD_OUT entries, keep them flagged
    - Fill missing seats_available with -1 (unknown)
    - Fill missing base_fare/taxes using the 88%/12% split of total_fare
    """
    if df.empty:
        return df
        
    df_clean = df.copy()
    
    if "seats_available" in df_clean.columns:
        df_clean["seats_available"] = df_clean["seats_available"].fillna(-1)
        
    if "total_fare" in df_clean.columns:
        if "base_fare" not in df_clean.columns:
            df_clean["base_fare"] = np.nan
        if "taxes" not in df_clean.columns:
            df_clean["taxes"] = np.nan
            
        mask_both = df_clean["base_fare"].isna() & df_clean["taxes"].isna()
        if mask_both.any():
            df_clean.loc[mask_both, "base_fare"] = (df_clean.loc[mask_both, "total_fare"] / 1.12).round(2)
            df_clean.loc[mask_both, "taxes"] = (df_clean.loc[mask_both, "total_fare"] - df_clean.loc[mask_both, "base_fare"]).round(2)
            
        mask_base = df_clean["base_fare"].isna() & ~df_clean["taxes"].isna()
        if mask_base.any():
            df_clean.loc[mask_base, "base_fare"] = (df_clean.loc[mask_base, "total_fare"] - df_clean.loc[mask_base, "taxes"]).round(2)
            
        mask_taxes = ~df_clean["base_fare"].isna() & df_clean["taxes"].isna()
        if mask_taxes.any():
            df_clean.loc[mask_taxes, "taxes"] = (df_clean.loc[mask_taxes, "total_fare"] - df_clean.loc[mask_taxes, "base_fare"]).round(2)
            
    return df_clean

def clean_fares(df: pd.DataFrame, outlier_method: str = "iqr") -> pd.DataFrame:
    """
    Full cleaning pipeline: dedup -> handle missing -> detect outliers.
    Returns cleaned DataFrame.
    """
    initial_rows = len(df)
    
    if initial_rows == 0:
        return df
        
    print(f"Cleaning {initial_rows} rows...")
    
    # 1. Remove duplicates
    df = remove_duplicates(df)
    dedup_rows = len(df)
    duplicates_removed = initial_rows - dedup_rows
    
    # 2. Handle missing data
    df = handle_missing_data(df)
    
    # 3. Detect outliers
    if outlier_method.lower() == "zscore":
        df = detect_outliers_zscore(df)
    else:
        df = detect_outliers_iqr(df)
        
    outliers_flagged = int(df["is_outlier"].sum()) if "is_outlier" in df.columns else 0
    
    # 4. Log stats
    print(f"Stats:")
    print(f"  - Total rows initial: {initial_rows}")
    print(f"  - Duplicates removed: {duplicates_removed}")
    print(f"  - Total rows final: {dedup_rows}")
    print(f"  - Outliers flagged: {outliers_flagged}")
    
    return df
