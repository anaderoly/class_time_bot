import pandas as pd
from datetime import datetime, date
from app.handlers.errors import FormatError, LogicError, DBError
from app.handlers.persistance import select_class_times
from app.tools.round import stable_round


REPORT_COMMAND = "Ученики"
ROUND = 2


def parse_dates(line: str) -> tuple[date, date]:
    s = line.strip().split()
    return (
        datetime.strptime(s[0], "%d.%m.%y").date(),
        datetime.strptime(s[1], "%d.%m.%y").date()
    )


def parse_request(request):
    request = request.replace(REPORT_COMMAND, "")

    try:
        start_dt, stop_dt = parse_dates(request)
    except:
        raise FormatError("Oшибка формата команды")

    if stop_dt < start_dt:
        raise LogicError("Ошибка диапазона дат")

    return start_dt, stop_dt


def get_class_times(user_id: int, start_dt: date, stop_dt: date):
    try:
        result = select_class_times(user_id, start_dt, stop_dt)
    except:
        raise DBError("Невозможно получить данные из базы")

    result = pd.DataFrame(result)
    if result.empty:
        raise LogicError("Нет данных за выбранный период")

    return result


def convert_to_report(df: pd.DataFrame) -> str:
    df = df.set_index("class_name")
    class_time = stable_round(df["class_time_h"], ROUND)
    class_time_md = class_time.rename_axis("Ученик").rename("Время").to_frame().to_string()

    return "\n\n".join([
        f"<pre>{class_time_md}</pre>",
        f"Общее время: {class_time.sum()} ч"
    ])


def get_report(user_text, user_id):
    try:
        start_dt, stop_dt = parse_request(user_text)
        result = get_class_times(user_id, start_dt, stop_dt)
        result = convert_to_report(result)
    except (FormatError, LogicError, DBError) as e:
        return str(e)
    except Exception as e:
        return f"Неизвестная ошибка: {e}"

    return result