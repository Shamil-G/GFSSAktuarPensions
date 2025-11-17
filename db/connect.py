import db_config as cfg
from gfss_parameter import LD_LIBRARY_PATH, platform
from util.logger import log
import oracledb

def init_session(connection, requestedTag_ignored):
    cursor = connection.cursor()
    cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'DD.MM.YYYY HH24:MI'")
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
    mistake = 0
    err_mess = ''
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt)
                recs = cursor.fetchall()
                for rec in recs:
                    results.append(rec)
            except oracledb.DatabaseError as e:
                error, = e.args
                mistake = 1
                err_mess = f"Oracle error: {error.code} : {error.message}"
                log.error(err_mess)
                log.error(f"ERROR with ------select------>\n{stmt}\n")
            finally:
                return mistake, results, err_mess


def select_one(stmt, args):
    mistake = 0
    err_mess = ''
    rec = []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                #log_outcoming.info(f"\nВыбираем данные: {stmt}")
                cursor.execute(stmt, args)
                rec = cursor.fetchone()
            except oracledb.DatabaseError as e:
                error, = e.args
                mistake = 1
                err_mess = f"Oracle error: {error.code} : {error.message}"
                log.error(f"ERROR with ------select------>\n{stmt}\n")
                log.error(err_mess)
            finally:
                return mistake, rec, err_mess


def plsql_execute(cursor, f_name, cmd, args):
    try:
        cursor.execute(cmd, args)
    except oracledb.DatabaseError as e:
        error, = e.args
        log.error(f"------execute------> ERROR. {f_name}. args: {args}")
        log.error(f"Oracle error: {error.code} : {error.message}")


def plsql_proc_s(f_name, proc_name, args):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            plsql_proc(cursor, f_name, proc_name, args)


def plsql_func_s(f_name, proc_name, args):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            return plsql_func(cursor, f_name, proc_name, args)


def plsql_proc(cursor, f_name, proc_name, args):
    try:
        cursor.callproc(proc_name, args)
    except oracledb.DatabaseError as e:
        error, = e.args
        # log.error(f"-----plsql-proc-----> ERROR. {f_name}. IP_Addr: {ip_addr()}, args: {args}")
        log.error(f"-----plsql-proc-----> ERROR. {f_name}. ARGS: {args}")
        log.error(f"Oracle error: {error.code} : {error.message}")


def plsql_func(cursor, f_name, func_name, args):
    ret = ''
    try:
        ret = cursor.callfunc(func_name, str, args)
    except oracledb.DatabaseError as e:
        error, = e.args
        log.error(f"-----plsql-func-----> ERROR. {f_name}. args: {args}")
        log.error(f"Oracle error: {error.code} : {error.message}")
    return ret


if __name__ == "__main__":
    print("Тестируем CONNECT блок!")
    con = get_connection()
    print("Версия: " + con.version)
    val = "Hello from main"
    con.close()
    _pool.close()

