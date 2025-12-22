import os
import pandas as pd
from dataclasses import dataclass, asdict
from supabase import create_client


supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"],
)


@dataclass
class LessonRecord:
    user_id: int
    work_date: str
    work_time_h: int
    lesson_num: int
    class_name: str
    claas_time_h: float


def df_to_records(df: pd.DataFrame, tg_user_id: int):
    records = []
    for _, row in df.iterrows():
        records.append(LessonRecord(
            user_id=tg_user_id,
            work_date=row["date"].isoformat(),
            work_time_h=row["total"],
            lesson_num=row["lesson"],
            class_name=row["class"],
            claas_time_h=row["time"]
        ))
    return records


def insert_table(df: pd.DataFrame, tg_user_id: int):
    records = df_to_records(df, tg_user_id)
    payload = [asdict(r) for r in records]
    supabase.table("lessons").insert(payload).execute()


def select_class_names(user_id: int, dates: list[str] = None):
    result = supabase.rpc("get_class_names", {"p_user_id": user_id, "p_exclude_dates": dates}).execute()
    return [r["class_name"] for r in result.data]
