from flask import Response
import urllib.parse
import pandas as pd 
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
import datetime
import io

from   util.logger import log
from   db.connect import get_connection
from   pivots.pivot_functions import flatten


report_name='Прогноз Базовой пенсии'
report_code='BP01'


# Визуализация расчета базовой пенсии
def get_stmt(scenario):
	return f"SELECT * FROM SOLIDARY_PENSION WHERE SCENARIO='{scenario}' order by pens_year, next_year, sex"


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


def export_to_excel(df_pivot, columns, scenario, filename=f"rep_{report_code}.xlsx"):
    s_date = datetime.datetime.now().strftime("%H:%M:%S")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df = df_pivot.copy()
        # df = df.fillna("")
        # df.to_excel(writer, sheet_name="Отчёт", index=False, startrow=4, header=False)

        workbook  = writer.book

        worksheet = workbook.add_worksheet('Отчёт')
        writer.sheets['Отчёт'] = worksheet

        sql_sheet = workbook.add_worksheet('SQL')
        writer.sheets['SQL'] = sql_sheet

        log.info(f"writer.book: {writer.book}")
        log.info(f"writer.sheets: {writer.sheets}")

        merge_format = workbook.add_format({
	        'bold':     False,
	        'border':   6,
	        'align':    'left',
	        'valign':   'vcenter',
	        'fg_color': '#FAFAD7',
	        'text_wrap': True
        })
        sql_sheet.merge_range('A1:I20', f'{get_stmt(scenario)}', merge_format)        
        worksheet.activate()
		
        # date_fmt = workbook.add_format({"num_format": "dd.mm.yyyy", "align": "center", "valign": "vcenter", "border": 1})
        title_name_report = workbook.add_format({'align': 'left', 'font_color': 'black', 'font_size': '14', "valign": "vcenter", "bold": True})

        money_fmt = workbook.add_format({"num_format": "# ### ### ##0.00", "align": "right", "valign": "vcenter", "border": 1})
        color_money_fmt = workbook.add_format({"num_format": "# ### ### ##0.00", "align": "right", "valign": "vcenter", "border": 1, 'fg_color': '#FAFAD7'})
        color_cnt_fmt = workbook.add_format({"num_format": "# ### ### ##0", "align": "right", "valign": "vcenter", "border": 1, 'fg_color': '#FAFAD7'})
        cnt_fmt = workbook.add_format({"num_format": "# ### ### ##0", "align": "right", "valign": "vcenter", "border": 1})
        count_fmt = workbook.add_format({"num_format": "# ### ### ##0", "align": "right", "valign": "vcenter", "border": 1})
        text_fmt = workbook.add_format({"align": "right", "border": 1})
        color_text_fmt = workbook.add_format({"align": "right", "border": 1, 'fg_color': '#FAFAD7' })
        color_text_fmt_center = workbook.add_format({"align": "center", "border": 1, 'fg_color': '#FAFAD7' })
        text_center_fmt = workbook.add_format({"align": "center", "border": 1})

        header_fmt = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "border": 1, "text_wrap": True, 'bg_color': '#D1FFFF'}) # Голубой
        subheader_fmt = workbook.add_format({"align": "center", "valign": "vcenter", "border": 1, 'bg_color': '#D1FFFF'}) # 'fg_color': '#FAFAD7' - желтый
        title_report_code = workbook.add_format({'align': 'right', 'font_size': '14', "valign": "vcenter", "bold": True})
        footer_fmt = workbook.add_format({'align': 'right', "valign": "vcenter", "italic": True}) # золотой фон
		
        worksheet.set_row(0, 24)
        worksheet.write(0, 0, f'{report_name}. Сценарий: {scenario}', title_name_report)
        worksheet.write(0, 8, report_code, title_report_code)

        # Заголовки first_row, first_col, last_row, last_col, data, cell_format
        # Шапка
        log.info(f'TYPE columns: {type(columns)}, columns {columns}')
        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 12)
        worksheet.set_column(2, 2, 6)
        worksheet.merge_range('A3:A4', 'Год назначения пенсии', header_fmt)
        worksheet.merge_range('B3:B4', 'Возраст назначения пенсии', header_fmt)
        worksheet.merge_range('C3:C4', 'Пол', header_fmt)
        col_idx = 3
        for i, col in enumerate(columns):
            worksheet.set_column(col_idx+i*3, col_idx+i*3, 12)
            worksheet.set_column(col_idx+i*3+1, col_idx+i*3+1, 19)
            worksheet.set_column(col_idx+i*3+2, col_idx+i*3+2, 14)
            worksheet.merge_range(2, col_idx +i*3,  2, col_idx + i*3 +2, col, header_fmt)
            worksheet.write(3, col_idx + i*3, 'Количество', subheader_fmt)
            worksheet.write(3, col_idx + i*3 + 1, 'Сумма', subheader_fmt)
            worksheet.write(3, col_idx + i*3 + 2, 'Среднее', subheader_fmt)
            # worksheet.write(0, 0, col, title_name_report)

        row_start = 4  # первая строка после шапки
        row_num = 0
        log.info(f'TYPE DF: {type(df)}')
        for row_num, record in enumerate(df):
            log.debug(f'row_num: {row_num}\n\tcolumns: {columns}\n\trecord: {record}')

            if row_num==0: 
                worksheet.merge_range('A5:C5', record['pens_year'], color_text_fmt_center)
            if row_num>0: 
                worksheet.write(row_start + row_num, 0, record['pens_year'], text_center_fmt)
                worksheet.write(row_start + row_num, 1, record['pens_age'], text_center_fmt)
                worksheet.write(row_start + row_num, 2, record['sex'], text_center_fmt)

            col_idx = 3
            for i, col in enumerate(columns):
                v__cnt = record.get(f'cnt_{col}','0').replace(' ','')
                v__sum = record.get(f'sum_{col}','0').replace(' ','')
                v__avg = record.get(f'avg_{col}','0').replace(' ','')

                if row_num==0:
                    worksheet.write(row_start + row_num, col_idx + i*3, '' if v__cnt=='' else Decimal(v__cnt), color_cnt_fmt)
                    worksheet.write(row_start + row_num, col_idx + i*3 + 1, '' if v__sum=='' else Decimal(v__sum), color_money_fmt)
                    worksheet.write(row_start + row_num, col_idx + i*3 + 2, '' if v__avg=='' else Decimal(v__avg), color_money_fmt)
                else:
                    worksheet.write(row_start + row_num, col_idx + i*3, '' if v__cnt=='' else Decimal(v__cnt), cnt_fmt)
                    worksheet.write(row_start + row_num, col_idx + i*3 + 1, '' if v__sum=='' else Decimal(v__sum), money_fmt)
                    worksheet.write(row_start + row_num, col_idx + i*3 + 2, '' if v__avg=='' else Decimal(v__avg), money_fmt)

        now = datetime.datetime.now()
        stop_time = now.strftime("%H:%M:%S")

        worksheet.write(1, 8, f'Дата формирования: {now.strftime("%d.%m.%Y ")}({s_date} - {stop_time})', footer_fmt)

        # Заморозим 4 строку и 1 колонку
        worksheet.freeze_panes(5, 3)
        # курсор в пределах таблицы
        #worksheet.set_selection(0, 0, row_start+row_num+1, col_idx)

        log.info(f'REPORT: {report_code}. Формирование отчета {filename} завершено ({s_date} - {stop_time}). Строк в отчете: {row_num+1}')

    safe_filename = urllib.parse.quote(filename)
    excel_bytes = output.getvalue()
    
    return Response(
        excel_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"}
    )


def get_solidary_items(scenario):
    stmt=get_stmt(scenario)
    log.info(f'GET SOLIDARY ITEMS. SCENARIO: {scenario}')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            stmt = get_stmt(scenario)
            log.debug(f'GET SOLIDARY ITEMS. STMT: {stmt}')
            cursor.execute(stmt)
            
            rows = cursor.fetchall()
            if not rows: 
                log.info(f'------->GET SOLIDARY ITEMS. not ROWS in SELECT:\n{get_stmt(scenario)}')
                return  {}, {}

            columns = [col[0].lower() for col in cursor.description]
            log.debug(f'------->GET SOLIDARY ITEMS\ncolumns: {columns}\nrows: {rows}\n<-------')
            df = pd.DataFrame(rows, columns=columns)
            if df is None or df.empty: return {}
            pivot, columns = build_pension_pivot(df)
            
            log.debug(f'GET SOLIDARY ITEMS. PIVOT: {pivot}')

            return pivot, columns


def get_solidary_pension_excel(params):
   scenario=params.get('scenario','')
   pivot, columns = get_solidary_items(scenario)
   log.info(f'get_base_pension_excel. params: {params}')
   return export_to_excel(pivot, columns, scenario)


def calculate_solidary_pension_in_db(scenario):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # планируем задачу в фоне через DBMS_SCHEDULER
            cmd = 'begin aktuar.forecast_solidary_pension.make(:scenario); end;'
            params = {'scenario':scenario}
            log.info(f"CALCULATE IN DB. START\t\nCMD: {cmd}\t\nPARAMS: {params}")
            cursor.execute(cmd, params)

            log.info(f"CALCULATE IN DB. FINISH. CMD: {cmd}")