import pandas as pd 
from    util.logger import log
from    db.connect import get_connection
import  pandas as pd
from   pivots.pivot_functions import flatten

# Визуализация расчета базовой пенсии
def get_stmt(scenario):
	return f"SELECT * FROM BASE_PENSION WHERE SCENARIO='{scenario}'"


import pandas as pd
import numpy as np


import pandas as pd

def build_pension_pivot(df: pd.DataFrame):
    """
    Строит pivot вида:
        cnt_YYYY, sum_YYYY, avg_YYYY
    Добавляет строку ИТОГО первой.
    Форматирует:
        cnt_*  → целые, разделитель тысяч пробелом
        sum_*, avg_* → 2 знака, разделитель тысяч пробелом
        NaN → ''
    Возвращает:
        rows (list of dict), years (list)
    """

    # ---------------------------------------------------------
    # 1. Лесенка: агрегируем cnt и sum по каждому next_year
    # ---------------------------------------------------------
    ladder = (
        df.groupby(["pens_year", "pens_age", "sex", "next_year"])
          .agg(
              cnt_ladder=("cnt", "sum"),
              sum_ladder=("sum_all", "sum")
          )
          .reset_index()
    )

    # ---------------------------------------------------------
    # 2. Pivot: cnt и sum — суммируем, avg считаем вручную
    # ---------------------------------------------------------
    cnt_pivot = ladder.pivot_table(
        index=["pens_year", "pens_age", "sex"],
        columns="next_year",
        values="cnt_ladder",
        aggfunc="sum"
    )

    sum_pivot = ladder.pivot_table(
        index=["pens_year", "pens_age", "sex"],
        columns="next_year",
        values="sum_ladder",
        aggfunc="sum"
    )

    # корректное среднее: sum / cnt
    avg_pivot = sum_pivot / cnt_pivot

    # ---------------------------------------------------------
    # 3. MultiIndex колонок → (year, metric)
    # ---------------------------------------------------------
    cnt_pivot.columns = pd.MultiIndex.from_product([cnt_pivot.columns, ["cnt"]])
    sum_pivot.columns = pd.MultiIndex.from_product([sum_pivot.columns, ["sum"]])
    avg_pivot.columns = pd.MultiIndex.from_product([avg_pivot.columns, ["avg"]])

    # ---------------------------------------------------------
    # 4. Объединяем в один DataFrame
    # ---------------------------------------------------------
    result = (
        cnt_pivot
        .join(sum_pivot)
        .join(avg_pivot)
        .sort_index(axis=1, level=0)
        .reset_index()  # вернёт pens_year, pens_age, sex в обычные колонки
    )

    result["sex"] = result["sex"].replace({"m": "м", "w": "ж"})

    # ---------------------------------------------------------
    # 5. Плоские имена колонок (без падения на служебных)
    # ---------------------------------------------------------
    flat_cols = []
    for col in result.columns:
        if isinstance(col, tuple):
            year, metric = col
            # нормальные метрические колонки: (год, 'cnt'/'sum'/'avg')
            if isinstance(year, (int, float)):
                flat_cols.append(f"{metric}_{int(year)}")
            else:
                # на всякий случай: если вдруг что-то нетипичное
                flat_cols.append(str(year) if metric in (None, "",) else f"{year}_{metric}")
        else:
            flat_cols.append(col)

    result.columns = flat_cols

    # ---------------------------------------------------------
    # 6. Список годов
    # ---------------------------------------------------------
    years = sorted(df["next_year"].unique())

    # ---------------------------------------------------------
    # 7. Форматтеры
    # ---------------------------------------------------------
    def fmt_int(v):
        if pd.isna(v):
            return ""
        return f"{int(v):,}".replace(",", " ")

    def fmt_float(v):
        if pd.isna(v):
            return ""
        return f"{float(v):,.2f}".replace(",", " ")

    cnt_cols = [c for c in result.columns if c.startswith("cnt_")]
    sum_cols = [c for c in result.columns if c.startswith("sum_")]
    avg_cols = [c for c in result.columns if c.startswith("avg_")]

    # ---------------------------------------------------------
    # 8. Строка ИТОГО — считаем ДО форматирования
    # ---------------------------------------------------------
    total_row = {
        "pens_year": "ИТОГО",
        "pens_age": "",
        "sex": "",
    }

    # суммы cnt и sum
    for col in cnt_cols:
        total_row[col] = result[col].astype(float).sum(skipna=True)

    for col in sum_cols:
        total_row[col] = result[col].astype(float).sum(skipna=True)

    # корректные avg = sum / cnt
    for year in years:
        c = f"cnt_{year}"
        s = f"sum_{year}"
        a = f"avg_{year}"
        cnt_val = total_row.get(c)
        sum_val = total_row.get(s)
        total_row[a] = (sum_val / cnt_val) if cnt_val not in (None, 0) else None

    # ---------------------------------------------------------
    # 9. Добавляем ИТОГО первой
    # ---------------------------------------------------------
    result = pd.concat([pd.DataFrame([total_row]), result], ignore_index=True)

    # ---------------------------------------------------------
    # 10. Форматируем ВСЁ
    # ---------------------------------------------------------
    for col in cnt_cols:
        result[col] = result[col].apply(fmt_int)

    for col in sum_cols + avg_cols:
        result[col] = result[col].apply(fmt_float)

    # текстовые поля
    for col in ("pens_year", "pens_age", "sex"):
        if col in result.columns:
            result[col] = result[col].astype(object).where(result[col].notna(), "")

    # ---------------------------------------------------------
    # 11. Возвращаем
    # ---------------------------------------------------------
    rows = result.to_dict(orient="records")
    return rows, years



def get_base_items(scenario):
    stmt=get_stmt(scenario)
    log.info(f'GET BASE ITEMS. SCENARIO: {scenario}')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            stmt = get_stmt(scenario)
            log.debug(f'GET BASE ITEMS. STMT: {stmt}')
            cursor.execute(stmt)
            
            rows = cursor.fetchall()
            if not rows: 
                log.info(f'------->GET BASE SOLIDARY ITEMS. not ROWS in SELECT:\n{get_stmt(scenario)}')
                return  {}, {}

            columns = [col[0].lower() for col in cursor.description]
            log.debug(f'------->GET BASE ITEMS\ncolumns: {columns}\nrows: {rows}\n<-------')
            df = pd.DataFrame(rows, columns=columns)
            if df is None or df.empty: return {}
            pivot, columns = build_pension_pivot(df)
            
            log.info(f'+++ GET BASE ITEMS. PIVOT: {pivot}')

            return pivot, columns
