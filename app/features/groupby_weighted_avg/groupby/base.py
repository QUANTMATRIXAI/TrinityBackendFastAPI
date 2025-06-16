# import pandas as pd


# def perform_groupby(df, identifiers, aggregations):
#     agg_funcs = {}
#     rank_measures = []

#     for measure, params in aggregations.items():
#         agg = params["agg"]
#         if agg == "weighted_mean":
#             weight_col = params.get("weight_by")
#             col_name = f"{measure}_weighted_mean"

#             def weighted_mean_func(x, measure=measure, weight_col=weight_col):
#                 measure_vals = x[measure]
#                 weight_vals = x[weight_col]
#                 return (measure_vals * weight_vals).sum() / weight_vals.sum() if weight_vals.sum() != 0 else None

#             agg_funcs[col_name] = (measure, weight_col, weighted_mean_func)

#         elif agg == "rank_pct":
#             rank_measures.append(measure)
#             agg_funcs[f"{measure}_for_rank"] = (measure, None, "first")

#         else:
#             col_name = f"{measure}_{agg}"
#             agg_funcs[col_name] = (measure, None, agg)

#     agg_dict = {
#         new_col: pd.NamedAgg(column=col, aggfunc=func)
#         for new_col, (col, _, func) in agg_funcs.items()
#     }

#     grouped = df.groupby(identifiers).agg(**agg_dict).reset_index()

#     for measure in rank_measures:
#         rank_col = f"{measure}_rank_pct"
#         grouped[rank_col] = grouped[f"{measure}_for_rank"].rank(pct=True)
#         grouped.drop(columns=[f"{measure}_for_rank"], inplace=True)

#     return grouped

from typing import List

def get_resample_options(current_freq: str) -> List[str]:
    freq_map = {
        "H": ["D", "W", "M"],     # Hourly → daily, weekly, monthly
        "D": ["W", "M", "Q"],     # Daily → weekly, monthly, quarterly
        "W": ["M", "Q"],          # Weekly → monthly, quarterly
        "M": ["Q", "A"],          # Monthly → quarterly, yearly
    }
    return freq_map.get(current_freq[0], [])  # Use only first char to generalize (e.g., "W-SUN" → "W")

import pandas as pd

def perform_groupby(df, identifiers, aggregations):
    agg_dict = {}
    weighted_means = []
    rank_measures = []

    identifiers = [col for col in identifiers if df[col].nunique() > 1]

    # Collect normal aggregations and prepare for special cases
    for measure, params in aggregations.items():
        if isinstance(params, str):
            params = {"agg": params}

        agg = params["agg"]

        if agg == "weighted_mean":
            weight_col = params.get("weight_by")
            if weight_col is None:
                raise ValueError(f"Missing 'weight_by' for weighted_mean of '{measure}'")
            weighted_means.append((measure, weight_col))
        elif agg == "rank_pct":
            rank_measures.append(measure)
            agg_dict[f"{measure}_for_rank"] = pd.NamedAgg(column=measure, aggfunc="first")
        else:
            agg_dict[f"{measure}_{agg}"] = pd.NamedAgg(column=measure, aggfunc=agg)

    # Initial groupby for standard aggregations
    df = df.reset_index() if any(x in df.index.names for x in identifiers) else df
    grouped = df.groupby(identifiers).agg(**agg_dict).reset_index()

    # Handle weighted mean separately
    if weighted_means:
        grouped_weights = []
        for keys, group in df.groupby(identifiers):
            row = dict(zip(identifiers, keys if isinstance(keys, tuple) else (keys,)))
            for measure, weight_col in weighted_means:
                wm_col = f"{measure}_weighted_mean"
                weight_vals = group[weight_col]
                measure_vals = group[measure]
                row[wm_col] = (
                    (measure_vals * weight_vals).sum() / weight_vals.sum()
                    if weight_vals.sum() != 0 else None
                )
            grouped_weights.append(row)
        grouped_weights_df = pd.DataFrame(grouped_weights)

        grouped = pd.merge(grouped, grouped_weights_df, on=identifiers, how="left")

    # Handle rank_pct
    for measure in rank_measures:
        rank_col = f"{measure}_rank_pct"
        grouped[rank_col] = grouped[f"{measure}_for_rank"].rank(pct=True)
        grouped.drop(columns=[f"{measure}_for_rank"], inplace=True)

    return grouped
