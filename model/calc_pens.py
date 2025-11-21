from    util.logger import log
from    flask import session
from    db.connect import get_connection, plsql_proc_s
import pandas as pd


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


def group_columns_by_year(columns):
    grouped = {}
    for col in columns:
        if '_' in col:
            year, _ = col.split('_', 1)
            grouped.setdefault(year, []).append(col)
    return grouped


def format_for_excel(df):
    for col in df.columns:
        if 'Сумма' in col:
            df[col] = df[col].apply(lambda x: float(str(x).replace(' ', '').replace(',', '.')) if pd.notna(x) else None)
    return df


def export_to_excel(df_pivot, grouped_columns, filename='report.xlsx'):
    df = format_for_excel(df_pivot.copy())
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Отчёт', index=False, startrow=2, header=False)

        workbook  = writer.book
        worksheet = writer.sheets['Отчёт']

        money_fmt = workbook.add_format({'num_format': '# ### ### ##0.00', 'align': 'right'})
        text_fmt = workbook.add_format({'align': 'center'})
        header_fmt = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        subheader_fmt = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})

        worksheet.merge_range(0, 0, 1, 0, 'Ид', header_fmt)
        worksheet.merge_range(0, 1, 1, 1, 'Дата рождения', header_fmt)
        col_idx = 2

        for year, cols in grouped_columns.items():
            worksheet.merge_range(0, col_idx, 0, col_idx + len(cols) - 1, year, header_fmt)
            for i, col in enumerate(cols):
                label = col.split('_', 1)[1]
                worksheet.write(1, col_idx + i, label, subheader_fmt)
            col_idx += len(cols)

        # Форматирование колонок
        for i, col in enumerate(df.columns):
            if 'Сумма' in col:
                worksheet.set_column(i, i, 18, money_fmt)
            else:
                worksheet.set_column(i, i, 14, text_fmt)


def get_pivot_table(df):
            if df.empty:  return [],[]
            # log.info(f'-------> DF:\n{df}\n<------')
            df_long = df.melt(id_vars=['ids', 'bd', 'year'], value_vars=['sum_pay', 'sum_incoming'], var_name='metric', value_name='value')

            df_pivot = df_long.pivot_table(
                index=['ids', 'bd'],
                columns=['year', 'metric'],
                values='value',
                aggfunc='first'
            )
            # for col in df_pivot.columns:
            #     if 'Сумма' in col:
            #         df_pivot[col] = df_pivot[col].apply(format_money)

            METRIC_RENAME_MAP = {
                'sum_incoming': 'Сумма входящая',
                'sum_pay': 'Сумма выплаты'
            }
            df_pivot.columns = pd.MultiIndex.from_tuples([
                (year, METRIC_RENAME_MAP.get(metric, metric))
                for year, metric in df_pivot.columns
            ])
            df_pivot.columns = [f'{year}_{metric}' for year, metric in df_pivot.columns]

            # log.info(f'-------> DF_COLUMNS:\n{df_pivot.columns}\n<------')

            # log.info(f'-------> DF_PIVOT.COLUMNS:\n{df_pivot.columns}\n<------')
            df_pivot = df_pivot[sort_columns(df_pivot.columns)]
            # log.info(f'-------> DF_PIVOT.GROUPED SORTED COLUMNS:\n{df_pivot.columns}\n<------')
            grouped_columns = group_columns_by_year(df_pivot.columns)
            # renamed_columns = rename_grouped_columns(grouped_columns)
            
            df_pivot = df_pivot.reset_index()

            df_pivot.rename(columns={'ids': 'Ид', 'bd': 'Дата рождения'}, inplace=True)

            # export_to_excel(df_pivot, grouped_columns)

            # log.info(f'-------> DF_PIVOT. COLUMNS:\n{grouped_columns}\n<------')
            df_pivot = df_pivot.where(pd.notna(df_pivot), '')
            # log.info(f'-------> DF_PIVOT.TO_DICT:\n{df_pivot.to_dict(orient='records')}\n<------')

            return (grouped_columns, df_pivot.to_dict(orient='records'))


def make_excel(filter):
    stmt = f"""
        select ids, to_char(bd,'dd.mm.yyyy') as bd, year, 
        -- sum_pay, incoming_sum
            to_char(sum_pay,'9G999G999G999D99') as sum_pay, 
            to_char(incoming_sum,'999G999G999G999D99') as sum_incoming
        from aktuar_pensioners pp
        where {filter}
        order by bd, year
    """
    log.info(f'make_excel')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(stmt)
            
            rows = cursor.fetchall()
            if not rows: return  [],[]

            columns = [col[0].lower() for col in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            (grouped_columns, rows) = get_pivot_table(df)    


def get_stmt(filter):
    return f"""
        select ids, to_char(bd,'dd.mm.yyyy') as bd, year, 
        -- sum_pay, incoming_sum
            to_char(sum_pay,'9G999G999G999D99') as sum_pay, 
            to_char(incoming_sum,'999G999G999G999D99') as sum_incoming
        from aktuar_pensioners pp
        where {filter}
        order by bd, year
    """

def get_pens_items(filter):
    log.info(f'GET PENS ITEMS.')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(get_stmt(filter))
            
            rows = cursor.fetchall()
            if not rows: 
                log.info(f'------->GET PENS ITEMS. not ROWS:\n{get_stmt(filter)}')
                return  [],[]

            columns = [col[0].lower() for col in cursor.description]
            log.debug(f'------->GET PENS YEAR ITEMS\ncolumns: {columns}\nrows: {rows}\n<-------')
            df = pd.DataFrame(rows, columns=columns)
            if df is None or df.empty: return [],[]
            return get_pivot_table(df)


def get_unique_year(filter):
    log.debug(f'GET UNIQUE YEAR.')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(get_stmt(filter))
            
            result = []
            records = cursor.fetchall()
            for rec in records:
                result.append(rec)
            log.debug(f'------ GET UNIQUE BIG REF NAME. RESULT:\n\t{result}')
            return result


def calculate_in_db(select_value, filter):
    plsql_proc_s('calculate_in_db', 'aktuar_pension.calculate_by_filter', (select_value, filter))
