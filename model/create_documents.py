import io
import pandas as pd
from reportlab.pdfgen import canvas  # для простого PDF-примера
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from flask import Response


def format_for_excel(df):
    for col in df.columns:
        if 'Сумма' in col:
            df[col] = df[col].apply(lambda x: float(str(x).replace(' ', '').replace(',', '.')) if pd.notna(x) else None)
    return df


def format_for_excel2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготовка DataFrame к экспорту в Excel:
    - Приведение названий колонок к читаемому виду
    - Приведение типов (даты, суммы)
    - Сортировка колонок по году/категории
    """
    df = df.copy()

    # Приведение названий колонок: убираем технические префиксы
    df.columns = [
        col.replace('_', ' ').strip().title()
        for col in df.columns
    ]

    # Приведение дат
    for col in df.select_dtypes(include=['datetime64']).columns:
        df[col] = df[col].dt.strftime('%d.%m.%Y')

    # Приведение сумм
    for col in df.columns:
        if 'Сумма' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

    # Сортировка колонок: сначала Ид, Дата рождения, потом остальные
    ordered_cols = []
    if 'Ид' in df.columns:
        ordered_cols.append('Ид')
    if 'Дата Рождения' in df.columns:
        ordered_cols.append('Дата Рождения')
    # добавляем остальные
    for col in df.columns:
        if col not in ordered_cols:
            ordered_cols.append(col)

    return df[ordered_cols]


def export_to_excel2(df_pivot, grouped_columns, filename='report.xlsx'):
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
        return filename


def export_to_excel(df_pivot, grouped_columns, filename="report.xlsx"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df = df_pivot.copy()
        df.to_excel(writer, sheet_name="Отчёт", index=False, startrow=2, header=False)

        workbook  = writer.book
        worksheet = writer.sheets["Отчёт"]

        money_fmt = workbook.add_format({"num_format": "# ### ### ##0.00", "align": "right"})
        text_fmt = workbook.add_format({"align": "center"})
        header_fmt = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "border": 1})
        subheader_fmt = workbook.add_format({"align": "center", "valign": "vcenter", "border": 1})

        # Заголовки
        worksheet.merge_range(0, 0, 1, 0, "Ид", header_fmt)
        worksheet.merge_range(0, 1, 1, 1, "Дата рождения", header_fmt)
        col_idx = 2
        for year, cols in grouped_columns.items():
            worksheet.merge_range(0, col_idx, 0, col_idx + len(cols) - 1, year, header_fmt)
            for i, col in enumerate(cols):
                label = col.split("_", 1)[1]
                worksheet.write(1, col_idx + i, label, subheader_fmt)
            col_idx += len(cols)

        # Форматирование колонок
        for i, col in enumerate(df.columns):
            if "Сумма" in col:
                worksheet.set_column(i, i, 18, money_fmt)
            else:
                worksheet.set_column(i, i, 14, text_fmt)

    excel_bytes = output.getvalue()
    return Response(
        excel_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def export_to_pdf(df_pivot, grouped_columns, filename="report.pdf"):
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(A4))

    # --- Заголовки ---
    header_top = ["Ид", "Дата рождения"]
    for year, cols in grouped_columns.items():
        header_top.extend([year] * len(cols))

    header_bottom = ["", ""]
    for year, cols in grouped_columns.items():
        for col in cols:
            label = col.split("_", 1)[1]
            header_bottom.append(label)

    data = [header_top, header_bottom]

    # --- Данные ---
    for _, row in df_pivot.iterrows():
        data.append([row[col] for col in df_pivot.columns])

    table = Table(data, repeatRows=2)
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
    ])
    table.setStyle(style)

    doc.build([table])
    pdf_bytes = output.getvalue()

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


