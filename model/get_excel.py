def get_excel(args: dict):
	stmt=get_stmt(args)

	log.debug(f'GET EXCEL. STMT:\n{stmt}')
	user_rfbn = args.get('user_rfbn', None)
	dep_name = args.get('user_dep_name', None)

	results = []
	mistake = 0
	err_mess = ''
	with get_connection() as connection:
		with connection.cursor() as cursor:
			try:
				cursor.execute(stmt)
				rows = cursor.fetchall()
			except oracledb.DatabaseError as e:
				error, = e.args
				mistake = 1
				err_mess = f"Oracle error: {error.code} : {error.message}"
				log.error(err_mess)
				log.error(f"ERROR with ------select------>\n{stmt}\n")
			
			if mistake>0:
				return  {},[]
			if not rows:
				log.info(f'GET EXCEL. Empty rows in stmt:\n\t{stmt}')
				return  {},[]

			columns = [col[0].lower() for col in cursor.description]
			df = pd.DataFrame(rows, columns=columns)
			log.debug(f"GET_EXCEL. COLUMNS: {columns} : {type(columns)}")
			
			return export_to_excel(df, columns, args, f"REP_{report_code}_{user_rfbn}_{dep_name}.xlsx")
