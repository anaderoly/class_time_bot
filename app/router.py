from app.commands.report import get_report, REPORT_COMMAND
from app.commands.inserter import insert_data


def route(user_text: str, user_id: int) -> str:
    if user_text.startswith(REPORT_COMMAND):
        return get_report(user_text, user_id)

    return insert_data(user_text, user_id)
