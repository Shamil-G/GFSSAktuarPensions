from    util.logger import log
from    db.connect import get_connection
import  pandas as pd
from    model.create_documents import export_to_excel, export_to_pdf
from    pivots.pivot_functions import *

def get_stmt(scenario, filter, limit_rows=1000):
    return f"""
        select ids, to_char(birth_date,'dd.mm.yyyy') as birth_date, year, 
        -- sum_pay, incoming_sum
            to_char(sum_pay,'9G999G999G999D99') as sum_pay, 
            to_char(incoming_sum,'999G999G999G999D99') as sum_incoming
        from aktuar_pensioners pp
        where {filter}
        and pp.scenario='{scenario}'
        FETCH FIRST {limit_rows} ROWS ONLY
    """


def sort_columns(columns):
    def extract_sort_key(col):
        try:
            year, metric = col.split('_', 1)
            metric_order = {
                'Сумма входящая': 0,
                'Сумма выплаты': 1,
                'Остаток': 2
            }
            return (int(year), metric_order.get(metric, 99))
        except Exception as e:
            log.warning(f'Ошибка сортировки колонки {col}: {e}')
            return (9999, 99)
    return sorted(columns, key=extract_sort_key)


def prepare_pivot(df):
    if df.empty:
        return pd.DataFrame(), {}

    df_long = df.melt(
        id_vars=['ids', 'birth_date', 'year'],
        value_vars=['sum_pay', 'sum_incoming'],
        var_name='metric',
        value_name='value'
    )

    df_pivot = df_long.pivot_table(
        index=['ids', 'birth_date'],
        columns=['year', 'metric'],
        values='value',
        aggfunc='first'
    )

    METRIC_RENAME_MAP = {
        'sum_incoming': 'Сумма входящая',
        'sum_pay': 'Сумма выплаты'
    }
    df_pivot.columns = pd.MultiIndex.from_tuples([
        (year, METRIC_RENAME_MAP.get(metric, metric))
        for year, metric in df_pivot.columns
    ])
    df_pivot.columns = [f'{year}_{metric}' for year, metric in df_pivot.columns]

    df_pivot = df_pivot[sort_columns(df_pivot.columns)]
    grouped_columns = group_columns_by_year(df_pivot.columns)

    df_pivot = df_pivot.reset_index()
    df_pivot.rename(columns={'ids': 'Ид', 'birth_date': 'Дата рождения'}, inplace=True)

    return df_pivot, grouped_columns


def get_pivot_table(df, type="data"):
    df_pivot, grouped_columns = prepare_pivot(df)

    match type:
        case "excel":
            return export_to_excel(df_pivot, grouped_columns)
        case "pdf":
            return export_to_pdf(df_pivot, grouped_columns)
        case _:
            df_pivot = df_pivot.where(pd.notna(df_pivot), "")
            return grouped_columns, df_pivot.to_dict(orient="records")


def make_document(scenario, filter, type):
    log.info(f'make_document')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            stmt = get_stmt(scenario, filter, 200)

            log.debug(f'MAKE_DOCUMENT. STMT: {stmt}')
            cursor.execute(stmt)
            
            rows = cursor.fetchall()
            if not rows: 
                log.info(f'MAKE_DOCUMENT. Empty rows in {stmt}')
                return  {},[]

            columns = [col[0].lower() for col in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            return get_pivot_table(df, type)


def get_pens_items(scenario, filter):
    log.info(f'GET PENS ITEMS. FILTER: {filter}')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            stmt = get_stmt(scenario, filter)
            log.debug(f'GET PENS ITEMS. STMT: {stmt}')
            # cursor.execute(get_stmt(filter))
            cursor.execute(stmt)
            
            rows = cursor.fetchall()
            if not rows: 
                log.info(f'------->GET PENS ITEMS. not ROWS:\n{get_stmt(scenario, filter)}')
                return  {},[]

            columns = [col[0].lower() for col in cursor.description]
            log.debug(f'------->GET PENS YEAR ITEMS\ncolumns: {columns}\nrows: {rows}\n<-------')
            df = pd.DataFrame(rows, columns=columns)
            if df is None or df.empty: return {},[]
            return get_pivot_table(df)


def get_unique_year(scenario, filter):
    log.debug(f'GET UNIQUE YEAR.')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(get_stmt(scenario, filter))
            
            result = []
            records = cursor.fetchall()
            for rec in records:
                result.append(rec)
            log.debug(f'------ GET UNIQUE BIG REF NAME. RESULT:\n\t{result}')
            return result


def calculate_in_db(scenario, filter):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # планируем задачу в фоне через DBMS_SCHEDULER
            cmd = 'begin aktuar.aktuar_pension.celery_task_calculate(:scenario, :filter); end;'
            params = {'scenario':scenario, 'filter': filter}
            log.info(f"CALCULATE IN DB. START\t\nCMD: {cmd}\t\nPARAMS: {params}")
            cursor.execute(cmd, params)

            log.info(f"CALCULATE IN DB. FINISH. CMD: {cmd}")
