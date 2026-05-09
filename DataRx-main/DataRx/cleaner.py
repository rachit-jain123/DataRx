'''
DataRx - A Command-Line Tool for Data Cleaning and Preprocessing
Developed by: Rachit Jain
GitHub: https://github.com/rachit-jain123/DataRx
Email: jrachit683@gmail.com

Module: cleaner.py
Description: This module handles all data cleaning operations on CSV files.
Operations supported:
1. Drop null values
2. Drop duplicate rows
3. Standardize column names (lowercase, remove spaces etc)
4. Fill missing values with mean/median/mode/constant
5. Generate cleaning summary and backup
'''

import numpy as np
import pandas as pd
from datetime import datetime
import os

def clean_csv(file, output, dropna=False, dropdupe=False, fix_cols=False, fillna="mean", columns=None):
    """
    Main function to clean a CSV file.

    Parameters:
    -----------
    file     : str  - Path to input CSV file
    output   : str  - Path to save cleaned CSV file
    dropna   : bool - Drop rows with missing values
    dropdupe : bool - Drop duplicate rows
    fix_cols : bool - Standardize column names
    fillna   : str  - Fill missing values with mean/median/mode/constant
    columns  : list - Specific columns to apply operations on
    """

    # Load Data
    df = pd.read_csv(file)
    original_shape = df.shape
    summary = []

    # Validate: At least one operation must be specified
    if not any([dropna, fillna, dropdupe, fix_cols]):
        raise ValueError(
            "[DataRx Error] No operation specified. "
            "Please use at least one of: --dropna, --fillna, --dropdupe, --fix-cols"
        )

    # Conflict Check: dropna + fillna cannot be used together
    if dropna and fillna:
        raise ValueError(
            "[DataRx Error] You cannot use both --dropna and --fillna together. "
            "Please choose only one missing value handling strategy."
        )

    # Column Validation
    if columns is not None and isinstance(columns, (list, tuple)) and len(columns) > 0:
        if all(len(col) == 1 for col in columns):
            joined = ''.join(columns)
            if joined in df.columns:
                columns = [joined]

        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"[DataRx Error] The following specified columns do not exist in the dataset: {missing_cols}"
            )
    else:
        columns = df.columns

    # Create Directories for Backups and Summaries
    os.makedirs("backups", exist_ok=True)
    os.makedirs("operation_summary", exist_ok=True)

    # Backup Original File Before Any Changes
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/{os.path.basename(file).split('.')[0]}_before_cleaning_{timestamp}.csv"
    df.to_csv(backup_path, index=False)

    summary.append("=" * 60)
    summary.append("         DataRx - Cleaning Summary Report")
    summary.append("         Developed by: Rachit Jain")
    summary.append("=" * 60)
    summary.append(f"Input File      : {file}")
    summary.append(f"Output File     : {output}")
    summary.append(f"Backup Saved To : {backup_path}")
    summary.append(f"Columns Targeted: {list(columns)}")
    summary.append("-" * 60)

    # Operation 1: Drop Rows with Missing Values
    if dropna:
        before = df.shape[0]
        if columns is not None and isinstance(columns, (list, tuple)) and len(columns) > 0:
            df.dropna(subset=columns, inplace=True)
            summary.append(f"[OK] Dropped rows with NA in columns: {list(columns)}")
        else:
            df.dropna(inplace=True)
            summary.append("[OK] Dropped rows with any missing values.")
        after = df.shape[0]
        summary.append(f"     Rows removed: {before - after}")

    # Operation 2: Drop Duplicate Rows
    if dropdupe:
        before = df.shape[0]
        df = df.drop_duplicates()
        after = df.shape[0]
        summary.append("[OK] Dropped duplicate rows.")
        summary.append(f"     Duplicates removed: {before - after}")

    # Operation 3: Fix/Standardize Column Names
    if fix_cols:
        old_cols = df.columns.tolist()
        cleaned_cols = [col.strip().lower().replace(" ", "_") for col in df.columns]

        final_cols = []
        seen = {}
        for col in cleaned_cols:
            if col not in seen:
                seen[col] = 1
                final_cols.append(col)
            else:
                seen[col] += 1
                final_cols.append(f"{col}_{seen[col]}")

        df.columns = final_cols
        renamed = [(o, n) for o, n in zip(old_cols, final_cols) if o != n]
        summary.append("[OK] Standardized column names.")
        summary.append(f"     Renamed: {renamed}")

    # Operation 4: Fill Missing Values
    if fillna is not None:
        if fillna is True:
            fillna = "mean"
            summary.append("[NOTE] No fillna strategy specified. Defaulting to 'mean'.")

        strategy = fillna.lower()
        numeric_cols = df.select_dtypes(include='number').columns

        if columns is not None and isinstance(columns, (list, tuple)) and len(columns) > 0:
            numeric_cols = [col for col in numeric_cols if col in columns]

        if strategy in ["mean", "median", "mode"]:
            fill_stats = {}
            for col in numeric_cols:
                if df[col].isnull().sum() > 0:
                    if strategy == "mean":
                        value = df[col].mean()
                    elif strategy == "median":
                        value = df[col].median()
                    else:
                        value = df[col].mode().iloc[0]
                    df[col] = df[col].fillna(value)
                    fill_stats[col] = round(value, 4)

            summary.append(f"[OK] Filled missing values using '{strategy}' strategy.")
            if fill_stats:
                summary.append(f"     Fill values used: {fill_stats}")

        else:
            try:
                constant = float(strategy)
                df.fillna(constant, inplace=True)
                summary.append(f"[OK] Filled all missing values with constant: {constant}")
            except (ValueError, TypeError):
                raise ValueError(
                    f"[DataRx Error] Invalid value for --fillna: '{fillna}'. "
                    f"Accepted values: 'mean', 'median', 'mode', or a numeric constant."
                )

    # Save Cleaned Data
    df.to_csv(output, index=False)

    summary.append("-" * 60)
    summary.append(f"[OK] Cleaned data saved to: {output}")
    summary.append(f"     Original shape : {original_shape}")
    summary.append(f"     Final shape    : {df.shape}")
    summary.append("=" * 60)

    # Save Summary Report
    summary_file = f"operation_summary/cleaning_summary_{timestamp}.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        for line in summary:
            f.write(line + "\n")

    summary.append(f"[OK] Summary saved to: {summary_file}")

    print("\n".join(summary))
    return