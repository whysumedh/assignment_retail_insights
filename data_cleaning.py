"""
Data cleaning script for May-2022.csv retail pricing dataset.
Handles missing values, standardizes platform names, extracts sizes, and calculates price metrics.
"""

import pandas as pd
import numpy as np
import os
import re
from pathlib import Path


def load_data(file_path: str) -> pd.DataFrame:
    """Load the CSV file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} records from {file_path}")
    return df


def extract_size_from_sku(sku: str) -> str:
    """Extract size from SKU pattern (e.g., 'Os206_3141_S' -> 'S')."""
    if pd.isna(sku) or not isinstance(sku, str):
        return None
    
    # Pattern: SKU ends with size like _S, _M, _L, _XL, _2XL, _3XL
    size_pattern = r'_([SMXL\d]+XL?)$'
    match = re.search(size_pattern, sku)
    if match:
        return match.group(1)
    return None


def standardize_platform_name(platform_col: str) -> str:
    """Standardize e-commerce platform column names."""
    # Remove ' MRP' suffix and convert to lowercase
    platform = platform_col.replace(' MRP', '').lower()
    # Handle special cases
    platform = platform.replace(' ', '_')
    return platform


def calculate_price_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate price differences and identify cheapest platform per product."""
    # Platform columns (excluding TP, MRP Old, Final MRP Old)
    platform_cols = [col for col in df.columns if 'MRP' in col and col not in ['MRP Old', 'Final MRP Old']]
    
    # Convert platform columns to numeric (handle string values)
    for col in platform_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Create a list of platform prices for each row
    platform_prices = []
    for col in platform_cols:
        platform_prices.append(df[col].values)
    
    platform_prices = np.array(platform_prices).T  # Transpose to get rows x platforms
    
    # Calculate metrics
    df['min_price'] = np.nanmin(platform_prices, axis=1)
    df['max_price'] = np.nanmax(platform_prices, axis=1)
    df['avg_price'] = np.nanmean(platform_prices, axis=1)
    df['price_range'] = df['max_price'] - df['min_price']
    
    # Find cheapest platform for each row
    cheapest_platforms = []
    for i, row in df.iterrows():
        prices = {col: row[col] for col in platform_cols if pd.notna(row[col])}
        if prices:
            cheapest = min(prices.items(), key=lambda x: x[1])
            # Extract platform name from column name
            platform_name = standardize_platform_name(cheapest[0])
            cheapest_platforms.append(platform_name)
        else:
            cheapest_platforms.append(None)
    
    df['cheapest_platform'] = cheapest_platforms
    df['cheapest_price'] = df['min_price']
    
    # Calculate savings compared to average
    df['savings_vs_avg'] = df['avg_price'] - df['min_price']
    df['savings_pct'] = (df['savings_vs_avg'] / df['avg_price'] * 100).round(2)
    
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Comprehensive data cleaning:
    - Handle missing values
    - Standardize platform names
    - Extract size from SKU
    - Calculate price metrics
    - Remove duplicates
    """
    print("Starting data cleaning...")
    initial_count = len(df)
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # 1. Extract size from SKU
    print("Extracting sizes from SKUs...")
    df_clean['Size'] = df_clean['Sku'].apply(extract_size_from_sku)
    
    # 2. Standardize platform column names (for easier access)
    platform_mapping = {}
    for col in df_clean.columns:
        if ' MRP' in col:
            new_name = standardize_platform_name(col)
            platform_mapping[col] = new_name
    
    # Keep original columns but add standardized access
    # We'll use original columns for calculations
    
    # 3. Handle missing values in critical columns
    print("Handling missing values...")
    
    # Fill missing weights with 0
    df_clean['Weight'] = df_clean['Weight'].fillna(0)
    
    # For platform MRP columns, we'll keep NaN as they represent unavailable products
    # But we'll filter out rows where ALL platform prices are missing
    platform_cols = [col for col in df_clean.columns if 'MRP' in col and col not in ['MRP Old', 'Final MRP Old']]
    df_clean = df_clean[df_clean[platform_cols].notna().any(axis=1)]
    
    # 4. Remove rows with invalid TP (Transfer Price)
    # Convert TP to numeric, handling any string values
    df_clean['TP'] = pd.to_numeric(df_clean['TP'], errors='coerce')
    df_clean = df_clean[(df_clean['TP'] > 0) & (df_clean['TP'].notna())]
    
    # 5. Standardize text fields
    print("Standardizing text fields...")
    if 'Catalog' in df_clean.columns:
        df_clean['Catalog'] = df_clean['Catalog'].str.strip()
    if 'Category' in df_clean.columns:
        df_clean['Category'] = df_clean['Category'].str.strip()
    
    # 6. Calculate price metrics
    print("Calculating price metrics...")
    df_clean = calculate_price_metrics(df_clean)
    
    # 7. Remove duplicates based on SKU (keep first occurrence)
    print("Removing duplicates...")
    duplicates_before = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['Sku'], keep='first')
    duplicates_removed = duplicates_before - len(df_clean)
    
    # 8. Add derived fields
    df_clean['has_price_variation'] = df_clean['price_range'] > 0
    df_clean['is_single_price'] = df_clean['price_range'] == 0
    
    # Final statistics
    final_count = len(df_clean)
    print(f"\nData cleaning completed!")
    print(f"Initial records: {initial_count}")
    print(f"Final records: {final_count}")
    print(f"Records removed: {initial_count - final_count}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Records with price variation: {df_clean['has_price_variation'].sum()}")
    print(f"Records with uniform pricing: {df_clean['is_single_price'].sum()}")
    
    return df_clean


def generate_summary_statistics(df: pd.DataFrame) -> dict:
    """Generate summary statistics for the cleaned dataset."""
    platform_cols = [col for col in df.columns if 'MRP' in col and col not in ['MRP Old', 'Final MRP Old']]
    
    summary = {
        'total_products': len(df),
        'total_skus': df['Sku'].nunique(),
        'total_styles': df['Style Id'].nunique(),
        'categories': df['Category'].value_counts().to_dict(),
        'catalogs': df['Catalog'].value_counts().to_dict(),
        'sizes': df['Size'].value_counts().to_dict(),
        'price_statistics': {
            'min_price_overall': float(df['min_price'].min()),
            'max_price_overall': float(df['max_price'].max()),
            'avg_price_overall': float(df['avg_price'].mean()),
            'median_price_overall': float(df['avg_price'].median())
        },
        'platform_analysis': {},
        'cheapest_platform_distribution': df['cheapest_platform'].value_counts().to_dict() if 'cheapest_platform' in df.columns else {}
    }
    
    # Platform-specific statistics
    for col in platform_cols:
        platform_name = standardize_platform_name(col)
        platform_data = df[col].dropna()
        if len(platform_data) > 0:
            summary['platform_analysis'][platform_name] = {
                'products_available': int(len(platform_data)),
                'min_price': float(platform_data.min()),
                'max_price': float(platform_data.max()),
                'avg_price': float(platform_data.mean()),
                'median_price': float(platform_data.median())
            }
    
    return summary


def save_cleaned_data(df: pd.DataFrame, output_path: str):
    """Save cleaned data to CSV."""
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")


def main():
    """Main function to run data cleaning pipeline."""
    # Get the data directory path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_file = project_root / 'data' / 'May-2022.csv'
    
    # Load data
    df = load_data(str(data_file))
    
    # Clean data
    df_clean = clean_data(df)
    
    # Generate summary
    summary = generate_summary_statistics(df_clean)
    
    # Save cleaned data
    output_file = script_dir / 'cleaned_data.csv'
    save_cleaned_data(df_clean, str(output_file))
    
    # Save summary as JSON for easy access
    import json
    summary_file = script_dir / 'data_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary statistics saved to {summary_file}")
    
    return df_clean, summary


if __name__ == "__main__":
    df_clean, summary = main()
    print("\nSample of cleaned data:")
    print(df_clean[['Sku', 'Style Id', 'Category', 'Size', 'min_price', 'max_price', 'cheapest_platform']].head(10))

