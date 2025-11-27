def group_columns_by_year(columns):
    grouped = {}
    for col in columns:
        if '_' in col:
            year, _ = col.split('_', 1)
            grouped.setdefault(year, []).append(col)
    return grouped