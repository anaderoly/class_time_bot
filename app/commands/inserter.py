from app.handlers.handler import handle
from app.handlers.persistance import select_class_names, insert_table


def insert_data(user_text, user_id):

    result, table = handle(user_text)
    if table is not None:
        try:
            class_names = select_class_names(user_id, table["date"].astype("str").unique().tolist())
            new_class_names = [c for c in table["class"].unique().tolist() if c not in class_names]
            if new_class_names:
                new_class_names_str = ", ".join(new_class_names)
                result += "\n"
                result += f"Найдены новые ученики: {new_class_names_str}"
            try:
                insert_table(table, user_id)
            except Exception as e:
                result = f"Ошибка сохранения: {e}"
        except Exception as e:
            result = f"Ошибка получения имен учеников: {e}"

    return result