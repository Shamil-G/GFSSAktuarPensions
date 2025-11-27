import datetime
from   util.logger import log
import  pandas as pd
from    db.connect import get_connection
from    util.logger import log
from    pivots.pivot_functions import *
import io
import pandas as pd
from flask import Response


report_name = 'Итоговый отчет по проекту пенсионных выплат'
report_code = 'SMM_01'


def get_stmt():
    stmt = """
        SELECT extract(year from o.birth_date) birth_year,
               ap.year, 
               sum(ap.incoming_sum ) incoming_sum,
               sum(ap.sum_pay) sum_pay,
               count(ap.ids) cnt_ids
        FROM aktuar_pensioners ap, actuar_pension_osnova o
        where ap.ids=o.ids
        group by ap.year, extract(year from o.birth_date)
    """
    return stmt


def export_to_excel(df_pivot, columns, filename=f"rep_{report_code}.xlsx"):
    s_date = datetime.datetime.now().strftime("%H:%M:%S")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df = df_pivot.copy()
        df = df.fillna("")
        # df.to_excel(writer, sheet_name="Отчёт", index=False, startrow=4, header=False)

        workbook  = writer.book

        worksheet = workbook.add_worksheet('Отчёт')
        sql_sheet = workbook.add_worksheet('SQL')

        merge_format = workbook.add_format({
            'bold':     False,
            'border':   6,
            'align':    'left',
            'valign':   'vcenter',
            'fg_color': '#FAFAD7',
            'text_wrap': True
        })
        sql_sheet.merge_range('A1:I10', f'{get_stmt()}', merge_format)        
        worksheet.activate()
        
        # date_fmt = workbook.add_format({"num_format": "dd.mm.yyyy", "align": "center", "valign": "vcenter", "border": 1})
        title_name_report = workbook.add_format({'align': 'left', 'font_color': 'black', 'font_size': '14', "valign": "vcenter", "bold": True})

        money_fmt = workbook.add_format({"num_format": "# ### ### ##0.00", "align": "right", "valign": "vcenter", "border": 1})
        count_fmt = workbook.add_format({"num_format": "# ### ### ##0", "align": "center", "valign": "vcenter", "border": 1})
        text_fmt = workbook.add_format({"align": "center", "border": 1})
        header_fmt = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "border": 1, "text_wrap": True, 'bg_color': '#D1FFFF'}) # Голубой
        subheader_fmt = workbook.add_format({"align": "center", "valign": "vcenter", "border": 1, 'bg_color': '#D1FFFF'}) # 'fg_color': '#FAFAD7' - желтый
        title_report_code = workbook.add_format({'align': 'right', 'font_size': '14', "valign": "vcenter", "bold": True})
        footer_fmt = workbook.add_format({'align': 'right', "valign": "vcenter", "italic": True}) # золотой фон
        
        worksheet.set_row(0, 24)
        worksheet.write(0, 0, report_name, title_name_report)
        worksheet.write(0, 6, report_code, title_report_code)

        # Заголовки first_row, first_col, last_row, last_col, data, cell_format
        worksheet.set_column(0, 0, 12)
        worksheet.merge_range(2, 0, 3, 0, "Год рождения", header_fmt)
        col_idx = 1

        for year, cols in columns.items():
            # if year == "birth" or 'birth_year' in cols:
            #     continue
            worksheet.merge_range(2, col_idx, 2, col_idx + len(cols) - 1, year, header_fmt)
            for i, col in enumerate(cols):
                metric = col.split("_", 1)[1]
                # log.info(f"metric: {metric}, col: {col}")
                worksheet.write(3, col_idx+i, metric, subheader_fmt)
                match metric:
                    case 'Входящая сумма': worksheet.set_column(col_idx+i, col_idx+i, 18)
                    case 'Сумма выплат': worksheet.set_column(col_idx+i, col_idx+i, 18)
                    case 'Количество выплат': worksheet.set_column(col_idx+i, col_idx+i, 18)
                    case _: worksheet.set_column(col_idx+i, col_idx+i, 12)
            col_idx += len(cols)

        row_start = 4  # первая строка после шапки
        row_num=0
        for row_num, (_, record) in enumerate(df.iterrows()):
            # log.info(f"WRITE RECORD. row_num: {row_num}, record: {record}")
            worksheet.write(row_start + row_num, 0, record["Год рождения"], text_fmt)
            col_idx = 1
            for year, cols in columns.items():
                for col in cols:
                    value = record[col]
                    metric = col.split("_", 1)[1]
                    match metric:
                        case "Входящая сумма": worksheet.write(row_start + row_num, col_idx, value, money_fmt)
                        case "Сумма выплат":   worksheet.write(row_start + row_num, col_idx, value, money_fmt)
                        case "Количество выплат": worksheet.write(row_start + row_num, col_idx, value, count_fmt)
                        case _: worksheet.write(row_start + row_num, col_idx, '-//-', text_fmt)
                    col_idx += 1


        now = datetime.datetime.now()
        stop_time = now.strftime("%H:%M:%S")

        worksheet.write(1, 6, f'Дата формирования: {now.strftime("%d.%m.%Y ")}({s_date} - {stop_time})', footer_fmt)

        # Заморозим 4 строку и 1 колонку
        worksheet.freeze_panes(4, 1)
        # курсор в пределах таблицы
        worksheet.set_selection(0, 0, row_start+row_num+1, col_idx)

    log.info(f'REPORT: {report_code}. Формирование отчета {filename} завершено ({s_date} - {stop_time}). Строк в отчете: {row_num+1}')

    excel_bytes = output.getvalue()
    return Response(
        excel_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def get_pivot(df):
    # Сортировка строк по birth_year
    df = df.sort_values(by="birth_year")

    pivot = df.pivot_table(
        index="birth_year",
        columns="year",
        values=["incoming_sum", "sum_pay", "cnt_ids"],
        aggfunc={"incoming_sum": "sum", "sum_pay": "sum", "cnt_ids": "sum"}
    )
    # Теперь pivot.columns — это MultiIndex: (metric, year)
    pivot = pivot.swaplevel(0, 1, axis=1).sort_index(axis=1)

    METRICS_ORDER = ["incoming_sum", "sum_pay", "cnt_ids"]
    YEARS_ORDER = sorted(df["year"].unique())

    pivot = pivot.reindex(
        columns=pd.MultiIndex.from_product([YEARS_ORDER, METRICS_ORDER])
    )

    # Красивые имена колонок (без индексных колонок)
    pivot.rename(columns={'incoming_sum': 'Входящая сумма', 'sum_pay': 'Сумма выплат', 'cnt_ids': 'Количество выплат'}, inplace=True)

    pivot.columns = [f"{year}_{metric}" for year, metric  in pivot.columns]

    # log.info(f'1. pivot.columns: {pivot.columns}')

    pivot = pivot.reset_index()
    # Индекс сброшен - появились индексные колонки, которые надо переименовать
    # Переименование после reset_index - так как колонки индекса birth_year и sex после этого переносятся в обычные колонки
    pivot.rename(columns={'birth_year': 'Год рождения', 'sex': 'Пол'}, inplace=True)

    # log.info(f'2. pivot.columns: {pivot.columns}')

    return pivot, group_columns_by_year(pivot.columns)


def make_report_summary_01():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            stmt = get_stmt()
            cursor.execute(stmt)

            rows = cursor.fetchall()
            if not rows: 
                log.info(f'MAKE_DOCUMENT. Empty rows in {stmt}')
                return  {},[]

            columns = [col[0].lower() for col in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            df_pivot, columns = get_pivot(df)
            
            return export_to_excel(df_pivot, columns)
