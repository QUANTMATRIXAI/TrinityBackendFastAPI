import pandas as pd

def get_filter_metadata_with_unique(df: pd.DataFrame) -> dict:
    metadata = {}
    for col in df.columns:
        col_data = df[col]
        unique_vals = col_data.dropna().unique().tolist()
        if len(unique_vals) > 100:
            unique_vals = unique_vals[:100] 
        if pd.api.types.is_numeric_dtype(col_data):
            metadata[col] = {
                "min": col_data.min(),
                "max": col_data.max(),
                "unique_values": unique_vals
            }
        else:
            metadata[col] = {
                "unique_values": unique_vals
            }
    return metadata


