from .deps import client
import pandas as pd
import datetime


async def save_groupby_result(validator_atom_id: str, file_key: str, df: pd.DataFrame):
    collection = client["groupby_db"]["groupby_results"]
    await collection.insert_one({
        "timestamp": datetime.datetime.utcnow(),
        "validator_atom_id": validator_atom_id,
        "file_key": file_key,
        "groupby_result": df.to_dict(orient="records")
    })
