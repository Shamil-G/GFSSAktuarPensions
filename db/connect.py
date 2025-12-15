import db_config as cfg
from gfss_parameter import LD_LIBRARY_PATH, platform
from util.logger import log
import oracledb

def init_session(connection, requestedTag_ignored):
    cursor = connection.cursor()
    cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'DD.MM.YYYY HH24:MI'")
    cursor.execute("ALTER SESSION SET NLS_NUMERIC_CHARACTERS = ', '")
    log.debug("--------------> Executed: ALTER SESSION SET NLS_DATE_FORMAT = 'DD.MM.YYYY HH24:MI'")
    cursor.close()

if platform == 'unix':
    oracledb.init_oracle_client(lib_dir=LD_LIBRARY_PATH)

_pool = oracledb.create_pool(user=cfg.username, 
                             password=cfg.password, 
                             host=cfg.host,
                             port=cfg.port,
                             service_name=cfg.service,
                             timeout=cfg.timeout, 
                             wait_timeout=cfg.wait_timeout,
                             max_lifetime_session=cfg.max_lifetime_session, 
                             expire_time=cfg.expire_time,
                             tcp_connect_timeout=cfg.tcp_connect_timeout, 
                             min=cfg.pool_min, 
                             max=cfg.pool_max, 
                             increment=cfg.pool_inc,
                             session_callback=init_session)
log.info(f"Пул соединенй БД Oracle создан. DB: {cfg.host}:{cfg.port}/{cfg.service}")


#@contextmanager
#def get_cursor():
#    conn = _pool.acquire()
#    try:
#        yield conn.cursor()
#    finally:
#        _pool.release(conn)


def get_connection():
    global _pool
    return _pool.acquire()


def close_connection(connection):
    global _pool
    _pool.release(connection)


def select(stmt):
    results = []
    err_message = ''
    status='success'
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt)
                recs = cursor.fetchall()
                for rec in recs:
                    results.append(rec)
            except oracledb.DatabaseError as e:
                error, = e.args
                status='fail'
                err_message = f'STMT: {stmt}\n\t{error.code} : {error.message}'
                log.error(f"------select------> ERROR\n{err_message}\n")
            finally:
                return status, results, err_message


def select_one(stmt, args):
    rec = []
    err_message = ''
    status='success'
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                #log_outcoming.info(f"\nВыбираем данные: {stmt}")
                cursor.execute(stmt, args)
                rec = cursor.fetchone()
            except oracledb.DatabaseError as e:
                error, = e.args
                status='fail'
                err_message = f'STMT: {stmt}\n\tARGS: {args}\n\t{error.code} : {error.message}'
                log.error(f"------select------> ERROR\n\t{err_message}")
                log.error(err_message)
            finally:
                return status, rec, err_message


def plsql_execute(cursor, proc_name, cmd, args):
    err_message = ''
    status='success'
    try:
        cursor.execute(cmd, args)
        log.debug(f"------execute------> INFO. {proc_name}\ncmd: {cmd}\nargs: {args}")
    except oracledb.DatabaseError as e:
        error, = e.args
        status='fail'
        err_message = f'{proc_name}:{cmd}\n\tARGS: {args}\n\t{error.code} : {error.message}'
        log.error(f"------execute------> ERROR\n\t{err_message}")
    finally:
        return status, f'{err_message}'


def plsql_execute_s(f_name, proc_name, args):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            return plsql_execute(cursor, f_name, proc_name, args)


def plsql_proc(cursor, f_name, proc_name, args):
    err_message = ''
    status='success'
    try:
        cursor.callproc(proc_name, args)
        log.debug(f"------plsql_proc------> INFO. \n\tf_name: {f_name}\n\tproc_name: {proc_name}\n\targs: {args}")
    except oracledb.DatabaseError as e:
        error, = e.args
        status='fail'
        err_message = f'{f_name}:{proc_name}\n\tARGS: {args}\n\t{error.code} : {error.message}'
        log.error(f"-----plsql-proc-----> ERROR. {err_message}")
    finally:
        return status, err_message


def plsql_proc_s(f_name, proc_name, args):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            return plsql_proc(cursor, f_name, proc_name, args)


def plsql_func(cursor, f_name, func_name, args):
    ret = ''
    err_mess = ''
    status='success'
    try:
        ret = cursor.callfunc(func_name, str, args)
    except oracledb.DatabaseError as e:
        error, = e.args
        status='fail'
        err_mess = f'{f_name}:{func_name}\n\tARGS: {args}\n\t{error.code} : {error.message}'
        log.error(f"-----plsql-func-----> ERROR. {err_mess}")
    finally:
        return status, ret, err_mess


def plsql_func_s(f_name, proc_name, args):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            return plsql_func(cursor, f_name, proc_name, args)


if __name__ == "__main__":
    print("Тестируем CONNECT блок!")
    con = get_connection()
    print("Версия: " + con.version)
    val = "Hello from main"
    con.close()
    _pool.close()

