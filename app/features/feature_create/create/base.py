import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL

def identify_columns_from_user(identifiers, measures, df):
    id_cols = [col for col in identifiers if col in df.columns]
    ms_cols = [col for col in measures if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    return id_cols, ms_cols


def calculate_residuals(df, y_var, x_vars):
    try:
        X = df[x_vars]
        y = df[y_var]

        X = (X - X.mean()) / X.std()
        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit()

        residuals = model.resid + y.mean()
        rsquared = model.rsquared

        return residuals, rsquared
    except Exception as e:
        raise Exception(f"Residual calculation failed: {str(e)}")



def compute_rpi(df, pivot_keys):

    if "PPU" not in df.columns:
        raise ValueError("PPU column not found. Ensure 'PPU' exists before RPI computation.")

    # if not columns:
    #     raise ValueError("Pivot keys must be provided for RPI operation.")
    
    # pivot_keys = columns
    d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
    d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
    if not d_date:
        raise ValueError("Date column not found in data.")

    pivot_df = df.pivot_table(index=[d_date, d_channel], columns=pivot_keys, values='PPU')

    df = pd.concat([df.set_index([d_date, d_channel]), pivot_df], axis=1).reset_index()

    if isinstance(pivot_df.columns, pd.MultiIndex):
        for col_tuple in pivot_df.columns:
            comp_col = "_".join(map(str, col_tuple)) + "_PPU"
            df[comp_col] = df[col_tuple]
            cond = True
            for i, key in enumerate(pivot_keys):
                cond &= (df[key] == col_tuple[i])
            df.loc[cond, comp_col] = np.nan
    else:
        for val in pivot_df.columns:
            comp_col = f"{val}_PPU"
            df[comp_col] = df[val]
            cond = (df[pivot_keys[0]] == val)
            df.loc[cond, comp_col] = np.nan

    try:
        df.drop(columns=pivot_df.columns, inplace=True)
    except Exception as e:
        pass  # Silent fail or log warning as needed

    # rename to RPI and compute own_ppu / competitor_ppu
    df.columns = [
        c.replace('_PPU','_RPI') if isinstance(c, str) and c.endswith('_PPU') else c
        for c in df.columns
    ]

    own_ppu = df["PPU"]
    for col in df.columns:
        if isinstance(col, str) and col.endswith('_RPI') and col != "PPU_RPI":
            df[col] = np.where(df[col] != 0, own_ppu / df[col], 0)

    new_col = [c for c in df.columns if isinstance(c, str) and c.endswith("_RPI") and c != "PPU_RPI"]
    return df, new_col






def apply_stl_outlier(df, columns):

    d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
    d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
    if not d_date or d_date not in df.columns:
        raise ValueError("Date column not found in data.")
    df[d_date] = pd.to_datetime(df[d_date], errors='coerce')
    outlier_keys = [d_channel] + (columns or [])

    final_df = df.copy().set_index(d_date)
    final_df[['residual', 'z_score_residual', 'is_outlier']] = np.nan, np.nan, 0

    for name, grp in final_df.groupby(outlier_keys):
        if len(grp) < 2:
            continue
        grp0 = grp.reset_index()
        try:
            res = STL(grp0['Volume'], seasonal=13, period=13).fit()
            grp0['residual'] = res.resid
            grp0['z_score_residual'] = (
                (grp0['residual'] - grp0['residual'].mean()) / grp0['residual'].std()
            )
            grp0['is_outlier'] = (grp0['z_score_residual'].abs() > 3).astype(int)

            for _, row in grp0.iterrows():
                dt = row[d_date]
                final_df.at[dt, 'residual'] = row['residual']
                final_df.at[dt, 'z_score_residual'] = row['z_score_residual']
                final_df.at[dt, 'is_outlier'] = row['is_outlier']
        except Exception as e:
            print(f"STL failed for {name}: {e}")

    final_df.reset_index(inplace=True)
    final_df.sort_values(by=d_date, inplace=True)

    # df = final_df

    df = final_df.drop(columns=["residual", "z_score_residual"], errors="ignore")

    
    new_col = 'is_outlier'


    return df, 'is_outlier'



















 
# def perform_transformation(df, operation: str, columns: list, identifiers: list, measures: list, extra_param: float = None):
#     id_cols, ms_cols = identify_columns_from_user(identifiers, measures, df)
#     new_col = None

#     try:
#         if operation == 'power':
#             new_cols = []
#             for col in columns:
#                 if col not in ms_cols:
#                     raise ValueError(f"Column {col} not a valid measure")
#                 new_col = f"{col}_power{extra_param}"
#                 df[new_col] = df[col] ** extra_param
#                 new_cols.append(new_col)
#             return df, new_cols

#         elif operation == 'log':
#             new_cols = []
#             for col in columns:
#                 if col not in ms_cols:
#                     raise ValueError(f"Column {col} not a valid measure")
#                 new_col = f"{col}_log"
#                 df[new_col] = np.log(df[col])
#                 new_cols.append(new_col)
#             return df, new_cols

#         elif operation == 'sqrt':
#             new_cols = []
#             for col in columns:
#                 if col not in ms_cols:
#                     raise ValueError(f"Column {col} not a valid measure")
#                 new_col = f"{col}_sqrt"
#                 df[new_col] = np.sqrt(df[col])
#                 new_cols.append(new_col)
#             return df, new_cols

#         elif operation == 'exp':
#             new_cols = []
#             for col in columns:
#                 if col not in ms_cols:
#                     raise ValueError(f"Column {col} not a valid measure")
#                 new_col = f"{col}_exp"
#                 df[new_col] = np.exp(df[col])
#                 new_cols.append(new_col)
#             return df, new_cols

#         elif operation == 'dummy':
#             new_cols = []
#             for col in columns:
#                 if col not in id_cols:
#                     raise ValueError(f"Column {col} not a valid identifier")
#                 new_col = f"{col}_dummy"
#                 df[new_col] = pd.Categorical(df[col]).codes
#                 new_cols.append(new_col)
#             return df, new_cols

#         elif operation == 'add':
#             col1, col2 = columns[:2]
#             if col1 not in ms_cols or col2 not in ms_cols:
#                 raise ValueError("Invalid measure columns")
#             new_col = f"{col1}_plus_{col2}"
#             df[new_col] = df[col1] + df[col2]

#         elif operation == 'subtract':
#             col1, col2 = columns[:2]
#             if col1 not in ms_cols or col2 not in ms_cols:
#                 raise ValueError("Invalid measure columns")
#             new_col = f"{col1}_minus_{col2}"
#             df[new_col] = df[col1] - df[col2]

#         elif operation == 'multiply':
#             col1, col2 = columns[:2]
#             if col1 not in ms_cols or col2 not in ms_cols:
#                 raise ValueError("Invalid measure columns")
#             new_col = f"{col1}_times_{col2}"
#             df[new_col] = df[col1] * df[col2]

#         elif operation == 'divide':
#             col1, col2 = columns[:2]
#             if col1 not in ms_cols or col2 not in ms_cols:
#                 raise ValueError("Invalid measure columns")
#             new_col = f"{col1}_dividedby_{col2}"
#             df[new_col] = df[col1] / df[col2]

#         elif operation == 'residual':
#             y_var = columns[0]
#             x_vars = columns[1:]
#             if y_var not in ms_cols or not all(x in ms_cols for x in x_vars):
#                 raise ValueError("Invalid Y or X columns")
#             residuals, rsq = calculate_residuals(df, y_var, x_vars)
#             new_col = f"Res_{y_var}"
#             df[new_col] = residuals



#         elif operation == 'rpi':
#             # Required columns: PPU, pivot_keys (passed via extra_param if needed)
#             if "PPU" not in df.columns:
#                 raise ValueError("PPU column not found. Ensure 'PPU' exists before RPI computation.")

#             if not columns:
#                 raise ValueError("Pivot keys must be provided for RPI operation.")
            
#             pivot_keys = columns
#             d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
#             d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
#             if not d_date:
#                 raise ValueError("Date column not found in data.")

#             pivot_df = df.pivot_table(index=[d_date, d_channel], columns=pivot_keys, values='PPU')

#             df = pd.concat([df.set_index([d_date, d_channel]), pivot_df], axis=1).reset_index()

#             if isinstance(pivot_df.columns, pd.MultiIndex):
#                 for col_tuple in pivot_df.columns:
#                     comp_col = "_".join(map(str, col_tuple)) + "_PPU"
#                     df[comp_col] = df[col_tuple]
#                     cond = True
#                     for i, key in enumerate(pivot_keys):
#                         cond &= (df[key] == col_tuple[i])
#                     df.loc[cond, comp_col] = np.nan
#             else:
#                 for val in pivot_df.columns:
#                     comp_col = f"{val}_PPU"
#                     df[comp_col] = df[val]
#                     cond = (df[pivot_keys[0]] == val)
#                     df.loc[cond, comp_col] = np.nan

#             try:
#                 df.drop(columns=pivot_df.columns, inplace=True)
#             except Exception as e:
#                 pass  # Silent fail or log warning as needed

#             # rename to RPI and compute own_ppu / competitor_ppu
#             df.columns = [
#                 c.replace('_PPU','_RPI') if isinstance(c, str) and c.endswith('_PPU') else c
#                 for c in df.columns
#             ]

#             own_ppu = df["PPU"]
#             for col in df.columns:
#                 if isinstance(col, str) and col.endswith('_RPI') and col != "PPU_RPI":
#                     df[col] = np.where(df[col] != 0, own_ppu / df[col], 0)

#             new_col = [c for c in df.columns if isinstance(c, str) and c.endswith("_RPI") and c != "PPU_RPI"]
#             return df, new_col
        

#         elif operation == 'marketshare':
#             if not columns:
#                 raise ValueError("Pivot keys must be provided for marketshare calculation.")
            
#             pivot_keys = columns
#             d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
#             d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
#             if not d_date:
#                 raise ValueError("Date column not found in data.")
            
#             # Compute category volume
#             catvol = (
#                 df.groupby([d_channel, d_date])['Volume']
#                   .sum().reset_index(name='CatVol')
#             )
#             df = df.merge(catvol, on=[d_channel, d_date], how='left')
#             df['NetCatVol'] = df['CatVol'] - df['Volume']
            
#             # Compute brand and channel sales
#             keys_for_brand = [d_channel] + pivot_keys
#             brand_totals = (
#                 df.groupby(keys_for_brand)['SalesValue']
#                   .sum().reset_index(name='BrandSales')
#             )
#             channel_totals = (
#                 df.groupby(d_channel)['SalesValue']
#                   .sum().reset_index(name='ChannelSales')
#             )
#             brand_totals = brand_totals.merge(channel_totals, on=[d_channel], how='left')
#             brand_totals['MarketShare_overall'] = (
#                 brand_totals['BrandSales'] / brand_totals['ChannelSales'] * 100
#             ).fillna(0)

#             df = df.merge(brand_totals[[*keys_for_brand, 'MarketShare_overall']], on=keys_for_brand, how='left')
#             new_col = 'MarketShare_overall'


#         elif operation == 'stl_outlier':
#             d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
#             d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
#             if not d_date or d_date not in df.columns:
#                 raise ValueError("Date column not found in data.")
#             df[d_date] = pd.to_datetime(df[d_date], errors='coerce')
#             outlier_keys = [d_channel] + (columns or [])

#             final_df = df.copy().set_index(d_date)
#             final_df[['residual', 'z_score_residual', 'is_outlier']] = np.nan, np.nan, 0

#             for name, grp in final_df.groupby(outlier_keys):
#                 if len(grp) < 2:
#                     continue
#                 grp0 = grp.reset_index()
#                 try:
#                     res = STL(grp0['Volume'], seasonal=13, period=13).fit()
#                     grp0['residual'] = res.resid
#                     grp0['z_score_residual'] = (
#                         (grp0['residual'] - grp0['residual'].mean()) / grp0['residual'].std()
#                     )
#                     grp0['is_outlier'] = (grp0['z_score_residual'].abs() > 3).astype(int)

#                     for _, row in grp0.iterrows():
#                         dt = row[d_date]
#                         final_df.at[dt, 'residual'] = row['residual']
#                         final_df.at[dt, 'z_score_residual'] = row['z_score_residual']
#                         final_df.at[dt, 'is_outlier'] = row['is_outlier']
#                 except Exception as e:
#                     print(f"STL failed for {name}: {e}")

#             final_df.reset_index(inplace=True)
#             final_df.sort_values(by=d_date, inplace=True)
#             df = final_df
#             new_col = 'is_outlier'


#         elif operation == 'kalman_filter':
#             d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
#             d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
#             if not d_date or d_date not in df.columns:
#                 raise ValueError("Date column not found in data.")
#             df[d_date] = pd.to_datetime(df[d_date], errors='coerce')
#             final_df = df.copy()
#             final_df.sort_values(by=d_date, inplace=True)
#             final_df.set_index(d_date, inplace=True)

#             def apply_kf(vals):
#                 kf = KalmanFilter(initial_state_mean=vals[0], n_dim_obs=1)
#                 means, _ = kf.filter(vals)
#                 return means.flatten()

#             final_df['FilteredVolume'] = np.nan
#             for _, grp in final_df.groupby([d_channel] + (columns or [])):
#                 grp_s = grp.sort_values(by=d_date).reset_index()
#                 try:
#                     filt = apply_kf(grp_s['Volume'].values)
#                     final_df.loc[grp_s['index'], 'FilteredVolume'] = filt
#                 except:
#                     continue

#             # Optional ratio flag: normalize by CatVol if present
#             if 'CatVol' in final_df.columns:
#                 final_df['FilteredVolume'] = np.where(
#                     final_df['CatVol'] != 0,
#                     final_df['FilteredVolume'] / final_df['CatVol'],
#                     0
#                 )

#             final_df.fillna(0, inplace=True)
#             final_df.reset_index(inplace=True)
#             df = final_df
#             new_col = 'FilteredVolume'

#         elif operation == 'standardize':
#             from sklearn.preprocessing import MinMaxScaler, StandardScaler

#             method = extra_param or "zscore"
#             if method == "zscore":
#                 scaler = StandardScaler()
#             elif method == "minmax":
#                 scaler = MinMaxScaler()
#             elif method == "none":
#                 scaler = None
#             else:
#                 raise ValueError("Unsupported standardization method")

#             transformed_cols = []
#             for col in columns:
#                 if col not in ms_cols:
#                     raise ValueError(f"{col} is not a valid measure column")

#                 if scaler:
#                     df[f"{col}_scaled"] = scaler.fit_transform(df[[col]])
#                 else:
#                     df[f"{col}_scaled"] = df[col]
#                 transformed_cols.append(f"{col}_scaled")

#             new_col = transformed_cols

#         elif operation == 'logistic':
#             def adstock_function(series, carryover):
#                 result = []
#                 prev = 0
#                 for val in series:
#                     curr = val + carryover * prev
#                     result.append(curr)
#                     prev = curr
#                 return np.array(result)

#             def logistic_function(x, gr, mp):
#                 return 1 / (1 + np.exp(-gr * (x - mp)))

#             if not extra_param or not isinstance(extra_param, dict):
#                 raise ValueError("Logistic transformation requires a dict with keys: gr, co, mp")

#             gr = extra_param.get("gr")
#             co = extra_param.get("co")
#             mp = extra_param.get("mp")

#             if gr is None or co is None or mp is None:
#                 raise ValueError("Missing logistic parameters")

#             transformed_cols = []
#             for col in columns:
#                 if col not in ms_cols:
#                     raise ValueError(f"{col} is not a valid measure column")

#                 adstocked = adstock_function(df[col].fillna(0), co)
#                 standardized = (adstocked - np.mean(adstocked)) / np.std(adstocked)
#                 df[f"{col}_logistic"] = logistic_function(standardized, gr, mp)
#                 transformed_cols.append(f"{col}_logistic")

#             new_col = transformed_cols





#         else:
#             raise ValueError(f"Unsupported operation: {operation}")

#         return df, new_col

#     except Exception as e:
#         raise Exception(f"Transformation failed: {str(e)}")
