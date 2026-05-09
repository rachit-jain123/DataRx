'''
DataRx - A Command-Line Tool for Data Cleaning and Preprocessing
Developed by: Rachit Jain
GitHub: https://github.com/rachit-jain123/DataRx
Email: jrachit683@gmail.com

Module: cli.py
Description: This is the main entry point of DataRx.
             All CLI commands are defined here using the Click library.
             Each command maps to a function in its respective module.

Commands Available:
    datarx clean          - Clean missing values, duplicates, fix column names
    datarx encode         - Encode categorical columns (label/onehot)
    datarx scale          - Scale numerical features (standard/minmax)
    datarx pca            - Apply PCA for dimensionality reduction
    datarx leakage        - Detect potential data leakage
    datarx eda            - Generate EDA report with graphs and summary
'''

import click
from datarx.cleaner import clean_csv
from datarx.encoder import encode_columns
from datarx.scaler import scale_columns
from datarx.pca import perform_pca
from datarx.leakage import detect_leakage
from datarx.eda import perform_eda
from datarx import __version__
import time


# ── Main CLI Group ─────────────────────────────────────────────────────────────
@click.group()
@click.version_option(version=__version__, prog_name="datarx")
def cli():
    """
    \b
    ╔══════════════════════════════════════════╗
    ║         DataRx - by Rachit Jain          ║
    ║   Data Cleaning & Preprocessing Tool     ║
    ║   GitHub: github.com/rachit-jain123      ║
    ╚══════════════════════════════════════════╝

    A command-line tool for automated data preprocessing.
    Clean, encode, scale, reduce, and analyze your CSV data
    with simple commands — no coding required.

    \b
    Recommended Workflow:
      1. datarx eda        → Explore your raw data
      2. datarx clean      → Handle nulls and duplicates
      3. datarx encode     → Encode categorical columns
      4. datarx scale      → Scale numerical features
      5. datarx pca        → Reduce dimensionality
      6. datarx leakage    → Check for data leakage
    """
    pass


# ── Command 1: CLEAN ───────────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", default="cleaned.csv",
              help="Output file name. Default: cleaned.csv")
@click.option("--dropna", is_flag=True,
              help="Drop rows with missing values.")
@click.option("--dropdupe", is_flag=True,
              help="Drop duplicate rows.")
@click.option("--fix-cols", is_flag=True,
              help="Standardize column names (lowercase, remove spaces etc).")
@click.option("--fillna", type=str, required=False, default=None,
              help="Fill null values using: mean, median, mode, or a constant. Mutually exclusive with --dropna.")
@click.option('--columns', multiple=True, default=None,
              help='Specific columns to operate on (comma-separated).')
def clean(file, output, dropna, dropdupe, fix_cols, fillna, columns):
    """
    Clean your CSV dataset.

    \b
    Examples:
      datarx clean data.csv --dropna --dropdupe --output cleaned.csv
      datarx clean data.csv --fillna mean --output cleaned.csv
      datarx clean data.csv --fillna median --columns col1,col2 --output cleaned.csv
    """
    # Handle --fillna passed without a value
    if fillna == "":
        fillna = True

    # Handle comma-separated columns passed as single string
    if columns and len(columns) == 1 and ',' in columns[0]:
        columns = [col.strip() for col in columns[0].split(',')]

    click.echo("\n[DataRx] Starting cleaning operation...")
    clean_csv(file, output, dropna, dropdupe, fix_cols, fillna, list(columns))
    click.secho(f"\n[DataRx] ✓ File cleaned successfully and saved to '{output}'", fg="green")


# ── Command 2: ENCODE ──────────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", default="encoded_output.csv",
              help="Output file name. Default: encoded_output.csv")
@click.option("--method", type=click.Choice(["label", "onehot"], case_sensitive=False),
              default='label', help="Encoding method: label or onehot. Default: label")
@click.option('--columns', multiple=True, default=None,
              help='Specific columns to encode (comma-separated). If not provided, all categorical columns are encoded.')
def encode(file, method, output, columns):
    """
    Encode categorical columns to numeric format.

    \b
    Examples:
      datarx encode cleaned.csv --method onehot --output encoded.csv
      datarx encode cleaned.csv --method label --columns Gender,City --output encoded.csv
    """
    # Handle comma-separated columns passed as single string
    if columns and len(columns) == 1 and ',' in columns[0]:
        columns = [col.strip() for col in columns[0].split(',')]

    click.echo(f"\n[DataRx] Starting {method} encoding...")
    encode_columns(file, output, method, list(columns))
    click.secho(f"\n[DataRx] ✓ {method} encoding done successfully! Saved to '{output}'", fg="green")


# ── Command 3: SCALE ───────────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", default="scaled_output.csv",
              help="Output file name. Default: scaled_output.csv")
@click.option("--method", type=click.Choice(["standard", "minmax"], case_sensitive=False),
              default="standard",
              help="Scaling method: standard or minmax. Default: standard")
@click.option("--columns", multiple=True,
              help="Specific columns to scale. If not provided, all numeric columns (excluding binary) are scaled.")
def scale(file, output, method, columns):
    """
    Scale numerical features for model readiness.

    \b
    Examples:
      datarx scale encoded.csv --method standard --output scaled.csv
      datarx scale encoded.csv --method minmax --columns Revenue,Profit --output scaled.csv
    """
    if method:
        method = method.lower()

    click.echo(f"\n[DataRx] Starting {method} scaling...")
    scale_columns(file, output, method, list(columns) if columns else None)
    click.secho(f"\n[DataRx] ✓ Columns scaled successfully using '{method}' method! Saved to '{output}'", fg="green")


# ── Command 4: PCA ─────────────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option('--components', type=int,
              help='Number of PCA components to keep.')
@click.option("--output", "-o", default="pca_output.csv",
              help="Output file name. Default: pca_output.csv")
@click.option('--retain', type=float,
              help='Fraction of variance to retain (e.g., 0.95). Mutually exclusive with --components.')
@click.option('--target', required=True,
              help='Target column name to exclude from PCA.')
def pca(file, output, target, components, retain):
    """
    Apply PCA for dimensionality reduction.

    \b
    Examples:
      datarx pca scaled.csv --retain 0.95 --target Profit --output pca.csv
      datarx pca scaled.csv --components 5 --target Profit --output pca.csv
    """
    click.echo("\n[DataRx] Starting PCA...")
    perform_pca(file, output, target, components, retain)
    click.secho(f"\n[DataRx] ✓ PCA applied successfully! Saved to '{output}'", fg="green")


# ── Command 5: LEAKAGE ─────────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option('--target', help="Name of the target column.")
@click.option('--threshold', type=float, default=0.85,
              help="Correlation threshold to flag high-risk features. Default: 0.85")
@click.option("--output", "-o", default="leakage_report.csv",
              help="Output file path. Default: leakage_report.csv")
def leakage(file, target, threshold, output):
    """
    Detect potential data leakage in your dataset.

    \b
    Examples:
      datarx leakage pca.csv --target Profit
      datarx leakage pca.csv --target Profit --threshold 0.9 --output leakage.csv
    """
    start_time = time.time()
    click.echo(f"\n[DataRx] Analysing data leakage with target: '{target}'...")

    try:
        report_df, summary_path = detect_leakage(file, target, threshold, output)
    except Exception as e:
        click.secho(f"\n[DataRx Error] {e}", fg="red")
        return

    click.echo(f"\n[DataRx] ✓ Leakage report saved to: {output}")
    click.echo(f"\n[DataRx] Top suspicious features:")
    click.echo(report_df[["feature", "score", "leak_risk"]].head(10).to_string(index=False))
    click.echo(f"\n[DataRx] Step summary saved to: {summary_path}")
    click.echo(f"\n[DataRx] Time taken: {round(time.time() - start_time, 2)} seconds")

    # Important reminder for the user
    click.secho("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="yellow")
    click.secho("  ⚠  Reminder: High Correlation ≠ Data Leakage", fg="yellow", bold=True)
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="yellow")
    click.secho(
        "  Some features are flagged due to strong correlation with the target.\n"
        "  This does not always mean data leakage.\n"
        "  Always use domain knowledge before removing any column.\n",
        fg="yellow"
    )


# ── Command 6: EDA ─────────────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--target", help="Optional: Name of the target column.")
@click.option("--output", "-o", default="eda_report.txt",
              help="Output file name. Default: eda_report.txt")
@click.option("--skip_graphs", is_flag=True,
              help="Skip graph generation for faster EDA on large datasets.")
def eda(file, target, output, skip_graphs):
    """
    Generate Exploratory Data Analysis (EDA) report.

    \b
    Examples:
      datarx eda data.csv --output eda_report.txt
      datarx eda data.csv --target Profit --output eda_report.txt
      datarx eda data.csv --skip_graphs --output eda_report.txt
    """
    start_time = time.time()
    click.echo(f"\n[DataRx] Running EDA on '{file}'...")

    try:
        summary_path = perform_eda(file, target, output, skip_graphs)
    except Exception as e:
        click.secho(f"\n[DataRx Error] {e}", fg="red")
        return

    click.echo(f"\n[DataRx] ✓ EDA summary saved to: {summary_path}")
    click.echo(f"[DataRx] Time taken: {round(time.time() - start_time, 2)} seconds")
    click.secho("\n[DataRx] ✓ EDA complete.", fg="green")


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cli()