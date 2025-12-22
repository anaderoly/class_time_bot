import numpy as np
import pandas as pd
from fractions import Fraction
from datetime import datetime, date


ROUND = 2


class FormatError(Exception):
    pass


class LogicError(Exception):
    pass


def strip(fn):
    def wrap(line):
        return fn(line.strip())
    return wrap


def stable_round(s: pd.Series, p: int) -> pd.Series:
    dec = 10**p
    floor = np.floor(s * dec) / dec
    rest = int(round((s.sum() - floor.sum()) * dec))

    if rest > 0:
        floor.iloc[np.argsort(s - floor, kind="stable")[-rest:]] += 1/dec

    return floor


@strip
def parse_date(line: str) -> tuple[str, date]:
    s = line.split()[0]
    return line[len(s):], datetime.strptime(s, "%d.%m.%y").date()


@strip
def parse_date_time(line: str) -> tuple[str, int]:
    s = line.split()[0]
    return line[len(s):], int(s[0])


@strip
def parse_num(line: str):
    s = line.split()[0]
    return line[len(s):], int(s[0])


@strip
def parse_time(line: str):
    s = line.split()[-1]
    f = Fraction(s) if "/" in s else s.replace(",", ".")
    return line[:-len(s)], float(f)


@strip
def parse_object(line: str):
    s = " ".join(line.split())
    s = s[:-1].rstrip() if s.endswith("Ф") else s
    s = s[:-1].rstrip() if s.endswith("М") else s
    return s, s.lower().capitalize()


def handle_text(text: str) -> pd.DataFrame:

    lines = [l.strip() for l in text.split("\n")]
    block = False
    rows = []

    for i, line in enumerate(lines):
        try:
            if not line.strip():
                block = False
                continue

            if not block:
                line, day = parse_date(line)
                line, day_time = parse_date_time(line)
                block = True
                continue

            if block:
                line, num = parse_num(line)
                line, time = parse_time(line)
                line, obj = parse_object(line)
                rows.append({
                    "date":day,
                    "total": day_time,
                    "lesson": num,
                    "class": obj,
                    "time": time
                })
        except:
            raise FormatError(f"Oшибка в строке {i+1}: {lines[i]}")

    return pd.DataFrame(rows)


def validate_df(df: pd.DataFrame):

    check: pd.Series = df.groupby("date")["total"].max() == df.groupby("date")["lesson"].nunique()
    if not check.all() == True:
        dates = ", ".join((map(str, check[~check].index.tolist())))
        raise LogicError(f"Общее время не совпадает c количеством уроков для: {dates}")

    check: pd.Series = df.groupby("date")["total"].max() == df.groupby("date")["time"].sum()
    if not check.all() == True:
        dates = ", ".join((map(str, check[~check].index.tolist())))
        raise LogicError(f"Общее время не совпадает c суммой времени уроков для: {dates}")


def prepare_report(df: pd.DataFrame) -> str:
    class_time = stable_round(df.groupby("class")["time"].sum(), ROUND)
    class_time_md = class_time.rename_axis("Ученик").rename("Время").to_frame().to_string()

    return "\n\n".join([
        f"<pre>{class_time_md}</pre>",
        f"Общее время: {class_time.sum()} ч"
    ])


def handle(text):
    try:
        df = handle_text(text)
        validate_df(df)
        return prepare_report(df), df
    except (FormatError, LogicError) as e:
        return str(e), None
    except Exception as e:
        return f"Неизвестная ошибка: {e}", None
