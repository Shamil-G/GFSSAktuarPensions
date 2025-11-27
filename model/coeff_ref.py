from    util.logger import log
from    db.connect import get_connection, plsql_execute


def get_coeff_items():
    stmt = """
        select name, value, version, active, descr
        from pens_params pp
        where pp.type='K'
        order by name, year
    """
    log.info(f'GET COEFF REF ITEMS.')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(stmt)
            
            result = []
            records = cursor.fetchall()
            for rec in records:
                res = {'name': rec[0], 'value': rec[1] or '0,00', 
                       'version': rec[2] or '0', 'active': rec[3],
                       'descr': rec[4]}
                result.append(res)
            log.debug(f'------ GET COEFF REF ITEMS. RESULT:\n\t{result}')
            return result


def save_coeff_value(ref_name, ref_value):
    stmt_update ="""
        begin update pens_params set value=:value where name=:ref_name and type='K'; commit; end;
    """
    value=0
    match ref_name:
        case 'count_year': value=int(float(ref_value))
        case 'first_year': value=int(float(ref_value))
        case 'pens_period': value=int(float(ref_value))
        case '': return
        case _: value=float(ref_value)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            args = {"value": value, "ref_name": ref_name}
            plsql_execute(cursor, "save_coeff_value", stmt_update, args )
            # try:
            #     cursor.execute(stmt_update, value=ref_value, ref_name=ref_name)
            # except:
            #     log.info(f'SAVE REF VALUE\n\tNAME: {ref_name}\n\tVALUE: {ref_value}')
            # finally:
            log.info(f'SAVE REF VALUE\n\tNAME: {args}')

