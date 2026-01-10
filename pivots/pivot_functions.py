def group_columns_by_year(columns):
    grouped = {}
    for col in columns:
        if '_' in col:
            year, _ = col.split('_', 1)
            grouped.setdefault(year, []).append(col)
    return grouped


def flatten(col):
    year, metric = col
    if isinstance(year, (int, float)):     # это pivot-колонка
        return f"{metric}_{int(year)}"
    return year                             # это pens_year / pens_age / sex

