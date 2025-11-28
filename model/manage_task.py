from db.connect import get_connection


def start_task(proc_name, task_id, params):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # планируем задачу в фоне через DBMS_SCHEDULER
            cursor.execute(f"""
                BEGIN
                  DBMS_SCHEDULER.create_job (
                    job_name        => 'TASK_{task_id}',
                    job_type        => 'PLSQL_BLOCK',
                    job_action      => 'BEGIN {proc_name}({task_id},{params}); END;',
                    start_date      => SYSTIMESTAMP,
                    enabled         => TRUE
                  );
                END;
            """)
    
def get_task_status(task_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT status FROM task_status WHERE task_id=:1", [task_id])
            status = cursor.fetchone()[0]
    return status
