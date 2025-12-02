from    util.logger import log
from    db.connect import get_connection
from decimal import Decimal

stmt_list_op = ""

def get_big_ref_items(scenario, parm_name):
    stmt = """
        select name, year, value
        from params pp
        where pp.name=coalesce(:parm_name,pp.name)
        and   pp.scenario=:scenario
        order by name, year
    """
    log.info(f'GET BIG REF ITEMS. PARM NAME: {parm_name}')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            args = {"scenario": scenario, "parm_name": parm_name}
            match parm_name:
                case _: cursor.execute(stmt, args)
            
            result = []
            records = cursor.fetchall()
            for rec in records:
                res = {'name': rec[0], 'year': rec[1], 'value': rec[2] or '0,00' }
                result.append(res)
            log.debug(f'------ GET BIG REF ITEMS. RESULT:\n\t{result}')
            return result


def get_unique_big_ref_name(scenario):
    stmt = f"""
        select unique name
        from params pp 
        where type='L'
        and   pp.scenario=:scenario
    """
    log.debug(f'GET UNIQUE BIG REF NAME.')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            args = {"scenario":scenario}
            cursor.execute(stmt, args)
            
            result = []
            records = cursor.fetchall()
            for rec in records:
                res = {'name': rec[0] }
                result.append(res)
            log.debug(f'------ GET UNIQUE BIG REF NAME. RESULT:\n\t{result}')
            return result

def save_ref_value(scenario, ref_name, ref_year, ref_value):
    value=0
    match ref_name:
        case 'участники': value=int(float(ref_value))
        case '': return
        case _: value=float(ref_value)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            args = {"scenario": scenario, "value": value, "ref_name": ref_name, "year": ref_year }
            try:
                cursor.execute('begin update params set value=:value where scenario=:scenario and name=:ref_name and year=:year; commit; end;', args)
            finally:
                        log.info(f'SAVE REF VALUE\n\tNAME: {ref_name}\n\tYEAR: {ref_year}\n\tVALUE: {ref_value}')

