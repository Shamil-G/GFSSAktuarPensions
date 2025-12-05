from    util.logger import log
from    db.connect import get_connection, plsql_proc_s
import  pandas as pd
from    model.create_documents import export_to_excel_2
from    pivots.pivot_functions import *
from    util.functions import get_scenario

def get_stmt(scenario, limit_rows=1000):
    return f"""
        select calc_year, year, 
            to_char(cnt_new_m,'9G999G999G999') as cnt_new_m, 
            to_char(cnt_new_w,'9G999G999G999') as cnt_new_w, 
            to_char(cnt_new_m+cnt_new_w,'9G999G999G999') as cnt_new_all, 


            to_char(cnt_curr_base,'9G999G999G999') as cnt_curr_base, 
            to_char(cnt_curr_solidary,'9G999G999') as cnt_curr_solidary, 

            to_char(sum_avg_base,'999G999G999G999D99') as sum_avg_base,
            to_char(sum_avg_solidary,'999G999G999G999D99') as sum_avg_solidary,

            to_char(sum_avg_base_new,'999G999G999G999D99') as sum_avg_base_new,
            to_char(sum_avg_solidary_new,'999G999G999G999D99') as sum_avg_solidary_new,
            to_char(sum_base,'999G999G999G999D99') as sum_base,
            to_char(sum_solidary,'999G999G999G999D99') as sum_solidary
        from base_solidary_pensioners pp
        where pp.scenario='{scenario}'
        FETCH FIRST {limit_rows} ROWS ONLY
    """


def prepare_base_solidary_pivot(df):
    if df.empty:
        return pd.DataFrame(), {}

    # Делаем melt (unpivot)
    # делаем melt: превращаем все метрики в строки
    df_melt = df.melt(
        id_vars=['year'],
        value_vars=[col for col in df.columns if col not in ["scenario","calc_year","year"]],
        var_name='metric_name',
        value_name='metric_value'
    )

    # pivot: метрики в строках, годы в колонках
    df_pivot = df_melt.pivot_table(
        index="metric_name",
        columns="year",
        values="metric_value",
        aggfunc="first",   # если нет дублей
        fill_value=''
    )

    METRIC_RENAME_MAP = {
        'metric_name': 'Показатель',
        'cnt_new_m' : 'Новых мужчин', 
        'cnt_new_w' : 'Новых женщин', 
        'cnt_new_all' : 'Всего мужчин и женщин', 


        'cnt_curr_base': 'Кол-во получателей базовой пенсии', 
        'cnt_curr_solidary': 'Кол-во получателей солидарной пенсии', 

        'sum_avg_base': 'Средний размер назначенной базовой пенсии',
        'sum_avg_solidary' :'Средний размер назначенной солидарной пенсии',

        'sum_avg_base_new': 'Средний размер новой базовой пенсии',
        'sum_avg_solidary_new': 'Средний размер новой солидарной пенсии',
        'sum_base': 'Размер базовой пенсии',
        'sum_solidary': 'Размер солидарной пенсии'
    }
    log.debug(f'PIVOT_COLUMNS: {df_pivot.columns}')

    df_pivot = df_pivot.reset_index()
    df_pivot["metric_name"] = df_pivot["metric_name"].replace(METRIC_RENAME_MAP)

    priority_order = [
        "Новых мужчин",
        "Новых женщин",
        "Всего мужчин и женщин",
        "Кол-во получателей базовой пенсии",
        "Кол-во получателей солидарной пенсии",
        'Средний размер назначенной базовой пенсии',
        'Средний размер новой базовой пенсии',
        'Средний размер назначенной солидарной пенсии',
        'Средний размер новой солидарной пенсии',
        'Размер базовой пенсии',
        'Размер солидарной пенсии'
    ]

    # задали приоритет для метрик
    df_pivot["metric_name"] = pd.Categorical(
        df_pivot["metric_name"],
        categories=priority_order,
        ordered=True
    )

    # сортировка по метрикам
    df_pivot = df_pivot.sort_values("metric_name")

    # сортировка по годам
    cols = ["metric_name"] + sorted(
        [c for c in df_pivot.columns if c != "metric_name"],
        key=lambda x: int(x)
    )
    df_pivot = df_pivot[cols]
    log.info(f'df_pivot: {df_pivot}')

    return df_pivot


def get_pivot_table(df, scenario, type="data"):
    df_pivot = prepare_base_solidary_pivot(df)
    log.info(f'NOW will be call export_to_excel_2')
    match type:
        case "excel":
            return export_to_excel_2(df_pivot, scenario, f'Base_Solidary.{scenario}.xlsx')
        case _:
            # df_pivot = df_pivot.where(pd.notna(df_pivot), "")
            return df_pivot.to_dict(orient="records")


def make_document(scenario, type):
    log.info(f'make_document')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            stmt = get_stmt(scenario, 200)

            log.debug(f'MAKE_DOCUMENT. STMT: {stmt}')
            cursor.execute(stmt)
            
            rows = cursor.fetchall()
            if not rows: 
                log.info(f'MAKE_DOCUMENT. Empty rows in {stmt}')
                return  {},[]

            columns = [col[0].lower() for col in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            return get_pivot_table(df, get_scenario(scenario), type)


def get_base_solidary_items(scenario):
    log.info(f'GET BASE SOLIDARY ITEMS. SCENARIO: {scenario}')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            stmt = get_stmt(scenario)
            log.debug(f'GET BASE SOLIDARY ITEMS. STMT: {stmt}')
            cursor.execute(stmt)
            
            rows = cursor.fetchall()
            if not rows: 
                log.info(f'------->GET BASE SOLIDARY ITEMS. not ROWS in SELECT:\n{get_stmt(scenario)}')
                return  {}

            columns = [col[0].lower() for col in cursor.description]
            log.debug(f'------->GET BASE SOLIDARY ITEMS\ncolumns: {columns}\nrows: {rows}\n<-------')
            df = pd.DataFrame(rows, columns=columns)
            if df is None or df.empty: return {}
            return get_pivot_table(df, scenario)


def calculate_base_solidary(scenario):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # планируем задачу в фоне через DBMS_SCHEDULER
            cmd =  f"""
                BEGIN
                  DBMS_SCHEDULER.create_job (
                    job_name        => 'TASK_CALCULATE_BASE_SOLIDARY',
                    job_type        => 'PLSQL_BLOCK',
                    job_action      => 'BEGIN aktuar.aktuar_base_solidary.calculate(''{scenario}''); END;',
                    start_date      => SYSTIMESTAMP,
                    enabled         => TRUE
                  );
                END;
            """
            log.info(f"CALCULATE BASE & SOLIDARY. CMD:\n{cmd}")
            cursor.execute(cmd)
