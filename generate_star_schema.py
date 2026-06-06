import pandas as pd
import os

def create_star_schema(input_csv, output_dir):
    # Read the dataset
    df = pd.read_csv(input_csv)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 1. Dim Time
    dim_time = df[['Month']].drop_duplicates().reset_index(drop=True)
    dim_time.insert(0, 'time_id', dim_time.index + 1)
    
    # 2. Dim Region
    dim_region = df[['Region']].drop_duplicates().reset_index(drop=True)
    dim_region.insert(0, 'region_id', dim_region.index + 1)
    
    # 3. Dim Segment
    dim_segment = df[['Segment']].drop_duplicates().reset_index(drop=True)
    dim_segment.insert(0, 'segment_id', dim_segment.index + 1)
    
    # 4. Dim Product
    dim_product = df[['Product']].drop_duplicates().reset_index(drop=True)
    dim_product.insert(0, 'product_id', dim_product.index + 1)

    # Merge to create Fact Table
    fact_df = df.copy()
    
    # Merge dimensions to get IDs
    fact_df = fact_df.merge(dim_time, on='Month', how='left')
    fact_df = fact_df.merge(dim_region, on='Region', how='left')
    fact_df = fact_df.merge(dim_segment, on='Segment', how='left')
    fact_df = fact_df.merge(dim_product, on='Product', how='left')
    
    # Select Fact columns
    fact_columns = [
        'time_id', 'region_id', 'segment_id', 'product_id',
        'Beginning_Customers', 'New_Customers', 'Lost_Customers', 'Net_Customers', 
        'Running_Total', 'Beginning_MRR', 'Expansion_MRR', 'Lost_MRR', 'Net_MRR', 'Running_Total_MRR',
        'Churn_Rate', 'Retention_Rate', 'Missing_Records', 
        'Duplicate_Customers', 'Invalid_Churn_Records', 'Data_Quality_Status', 
        'Last_Updated_Date'
    ]
    fact_churn = fact_df[fact_columns].copy()
    fact_churn.insert(0, 'fact_id', fact_churn.index + 1)
    
    # Save dimensions and fact table to CSV files
    dim_time.to_csv(os.path.join(output_dir, 'dim_time.csv'), index=False)
    dim_region.to_csv(os.path.join(output_dir, 'dim_region.csv'), index=False)
    dim_segment.to_csv(os.path.join(output_dir, 'dim_segment.csv'), index=False)
    dim_product.to_csv(os.path.join(output_dir, 'dim_product.csv'), index=False)
    fact_churn.to_csv(os.path.join(output_dir, 'fact_churn.csv'), index=False)
    
    print(f"Star schema successfully created in '{output_dir}' directory.")
    print(f"Dim Time: {len(dim_time)} rows")
    print(f"Dim Region: {len(dim_region)} rows")
    print(f"Dim Segment: {len(dim_segment)} rows")
    print(f"Dim Product: {len(dim_product)} rows")
    print(f"Fact Churn: {len(fact_churn)} rows")

if __name__ == "__main__":
    input_file = "customer_churn_governance_dataset.csv"
    output_directory = "star_schema_data"
    create_star_schema(input_file, output_directory)
