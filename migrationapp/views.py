from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
import psycopg2
from psycopg2 import extras
import urllib
import logging
import pyodbc
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import psycopg2
import mysql.connector

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def connect_to_postgresql():
    return psycopg2.connect(
        dbname="dmv_output",
        user="chandru_s",
        password="1233",
        host="localhost",
        port="5432")

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            create_user(username, email, password)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return HttpResponse(f"Failed to create user. Please try again. Error: {e}")

        return redirect('login')

    return render(request, 'migrationapp/signin.html')

def create_user(username, email, password):
    hashed_password = make_password(password)
    conn_pg = connect_to_postgresql()
    cur = conn_pg.cursor()

    try:
        cur.execute("SELECT * FROM users WHERE user_name = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()
        if existing_user:
            raise Exception("User already exists")
        
        cur.execute("INSERT INTO users (user_name, email, password, time_log) VALUES (%s, %s, %s, %s)",
                    (username, email, hashed_password, datetime.now()))
        conn_pg.commit()
    except Exception as e:
        conn_pg.rollback()
        logger.error(f"Database error: {e}")
        raise e
    finally:
        cur.close()
        conn_pg.close()

def data_catalogue(request):
    if request.method == 'POST':

        database_operation = request.POST.get("database_operation")

        if database_operation == "fetch_data":
            database_type = request.POST.get('database_name')
            if database_type == 'Postgres':
                data = retrieve_data_postgres()
            elif database_type == 'MySql':
                data = retrieve_data_mysql()
            else:
                data = []

        elif database_operation == "delete_records":
            print("deleted")
            delete_records()

            data = []
    else:
        data = []

    return render(request, 'migrationapp/data_catalogue.html', {'data': data})

def connect_to_postgresql():
    return psycopg2.connect(
        dbname="dmv_output",
        user="chandru_s",
        password="1233",
        host="localhost",
        port="5432"
    )

def connect_to_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1233",
        database="datamig"
    )

def delete_records():
    conn = connect_to_postgresql()  # Establish connection
    with conn.cursor() as cursor:
        cursor.execute("truncate table public.metadata;")
        
    conn.commit()
    conn.close()

    return []

def retrieve_data_postgres():
    conn = connect_to_postgresql()  # Establish connection
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT object_database, object_schema, object_type, object_name, object_size, time_log
            FROM public.metadata
        """)
        metadata_records = cursor.fetchall()

    conn.close()  # Close connection after fetching data
    # Convert records to a list of dictionaries
    records = [
        {
            'object_database': row[0],
            'object_schema': row[1],
            'object_type': row[2],
            'object_name': row[3],
            'object_size': row[4],
            'time_log': row[5]
        }
        for row in metadata_records
    ]
    return records

def retrieve_data_mysql():
    conn = connect_to_mysql()  # Establish connection
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM metadata")
    records = cursor.fetchall()
    conn.close()  # Close connection after fetching data
    return records

def board(request):
    return render(request, 'migrationapp/board.html')

def login(request):
    scan_message = None
    if request.method == "POST":
        print("hii....")
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        print(username_or_email)

        logger.debug(f"Received login attempt for username or email: {username_or_email}")

        user = get_user_by_username_or_email(username_or_email)

        if user:
            logger.debug(f"User found: {user}")
            if check_password(password, user[3]):  # Assuming the password is stored at index 3
                logger.debug("Password check passed.")
                request.session['user_id'] = user[0]  # Store user ID in session
                print("valid user..")
                return redirect("board")
            else:
                logger.debug("Password check failed.")
                scan_message = "Invalid Credentials."
                
        else:
            logger.debug("User not found.")
            scan_message = "Invalid Credentials."
            print("invalid......")
        return redirect("login")

    return render(request, 'migrationapp/login.html', {'scan_message': scan_message})




def get_user_by_username_or_email(username_or_email):
    conn_pg = connect_to_postgresql()
    cur = conn_pg.cursor()
    user = None
    try:
        cur.execute("SELECT * FROM users WHERE user_name = %s", (username_or_email,))
        user = cur.fetchone()
        if not user:
            cur.execute("SELECT * FROM users WHERE email = %s", (username_or_email,))
            user = cur.fetchone()
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        cur.close()
        conn_pg.close()

    return user


def scan_and_store_data(request):
    if request.method == "POST":
        conn_source = request.POST.get("conn_source")
        target_db_type = request.POST.get("target_db_type")
        db_type = request.POST.get("db_type")
        database = request.POST.get("db_name")
        password = request.POST.get("db_password")
        user = request.POST.get("db_username")
        host = request.POST.get("db_server")


        print("=================================")
        print(target_db_type)
        print(db_type)
        print(database)
        print(password)
        print(user)
        print(host)


        print("===============================")


        # Define the target database connection
        if target_db_type == 'postgresql':
            conn_pg = connect_to_postgresql()
        elif target_db_type == 'mysql':
            conn_pg = connect_to_mysql()
        else:
            return HttpResponse("Invalid target database type")

        
        try:
            cur = conn_pg.cursor()
            # Read existing records from the MetaData table
            cur.execute("SELECT object_database, object_schema, object_type, object_name, object_size FROM metadata")
            existing_records = cur.fetchall()

            existing_records = []  # Define a list to store existing records (if needed)

            # Iterate over SQL queries and process each result set
            if db_type == 'sqlserver':
                quoted_conn_str_sql_server = urllib.parse.quote_plus(
                    f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password}'
                )
                engine_sql_server = create_engine(f'mssql+pyodbc:///?odbc_connect={quoted_conn_str_sql_server}')

                sql_server_query = {
                    'Database': "SELECT DB_NAME() AS object_database;",
                    'Table': "SELECT DB_NAME() AS object_database, TABLE_SCHEMA AS object_schema, TABLE_NAME AS object_name, 'Table' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';",
                    'View': "SELECT DB_NAME() AS object_database, TABLE_SCHEMA AS object_schema, TABLE_NAME AS object_name, 'View' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.VIEWS;",
                    'Function': "SELECT DB_NAME() AS object_database, ROUTINE_SCHEMA AS object_schema, ROUTINE_NAME AS object_name, 'Function' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE = 'FUNCTION';",
                    'Stored_Procedure': "SELECT DB_NAME() AS object_database, ROUTINE_SCHEMA AS object_schema, ROUTINE_NAME AS object_name, 'Stored_Procedure' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE = 'PROCEDURE';",
                    'Trigger': "SELECT DB_NAME() AS object_database, OBJECT_SCHEMA_NAME(parent_id) AS object_schema, OBJECT_NAME(parent_id) AS object_name, 'Trigger' AS object_type, 'Unknown size' AS size FROM sys.triggers;",
                    'Index': "SELECT DB_NAME() AS object_database, OBJECT_SCHEMA_NAME(object_id) AS object_schema, name AS object_name, 'Index' AS object_type, 'Unknown size' AS size FROM sys.indexes;"
                }

                for query_type, query in sql_server_query.items():
                    df = pd.read_sql(query, engine_sql_server)
                    for index, row in df.iterrows():
                        object_database = row.get('object_database')
                        object_schema_name = row.get('object_schema')
                        object_type = row.get('object_type')
                        object_name = row.get('object_name')
                        object_size = row.get('size', 'Unknown size')
                        print(row)
                        if object_name is not None and \
                                (object_database, object_schema_name, object_type, object_name, object_size) not in existing_records:
                            insert_sql = """
                                            INSERT INTO metadata (object_database, object_schema, object_type, object_name, object_size) 
                                            VALUES (%s, %s, %s, %s, %s)
                                        """
                            cur.execute(insert_sql, (object_database, object_schema_name, object_type, object_name, object_size))
                            existing_records.append((object_database, object_schema_name, object_type, object_name, object_size))

            elif db_type == 'mysql':
                mysql_conn = mysql.connector.connect(
                    host=host, user=user, password=password, database=database
                )
                mysql_cursor = mysql_conn.cursor(dictionary=True)

                sql_query = {
                    'Table': "SELECT TABLE_SCHEMA AS object_schema, TABLE_NAME AS object_name, 'Table' AS object_type, 'Unknown size' AS size FROM information_schema.tables WHERE TABLE_TYPE = 'BASE TABLE';",
                    'View': "SELECT TABLE_SCHEMA AS object_schema, TABLE_NAME AS object_name, 'View' AS object_type, 'Unknown size' AS size FROM information_schema.views;",
                    'Function': "SELECT ROUTINE_SCHEMA AS object_schema, ROUTINE_NAME AS object_name, 'Function' AS object_type, 'Unknown size' AS size FROM information_schema.routines WHERE ROUTINE_TYPE = 'FUNCTION';",
                    'Stored_Procedure': "SELECT ROUTINE_SCHEMA AS object_schema, ROUTINE_NAME AS object_name, 'Stored_Procedure' AS object_type, 'Unknown size' AS size FROM information_schema.routines WHERE ROUTINE_TYPE = 'PROCEDURE';",
                    'Trigger': "SELECT TRIGGER_SCHEMA AS object_schema, TRIGGER_NAME AS object_name, 'Trigger' AS object_type, 'Unknown size' AS size FROM information_schema.triggers;",
                    'Index': "SELECT table_schema AS object_schema, table_name AS object_name, 'Index' AS object_type, 'Unknown size' AS size FROM information_schema.statistics WHERE index_name = 'PRIMARY';"
                }

                for query_type, query in sql_query.items():
                    mysql_cursor.execute(query)
                    for row in mysql_cursor.fetchall():
                        object_database = database
                        object_schema = row['object_schema'] if row.get('object_schema') is not None else ''
                        object_name = row['object_name'] if row.get('object_name') is not None else ''
                        object_type = row['object_type'] if row.get('object_type') is not None else ''
                        object_size = row['size'] if row.get('size') is not None else 'Unknown size'
                        print(row)
                        if object_name is not None and \
                                (object_database, object_schema_name, object_type, object_name, object_size) not in existing_records:
                            insert_sql = """
                                            INSERT INTO metadata (object_database, object_schema, object_type, object_name, object_size) 
                                            VALUES (%s, %s, %s, %s, %s)
                                        """
                            cur.execute(insert_sql, (object_database, object_schema_name, object_type, object_name, object_size))
                            existing_records.append((object_database, object_schema_name, object_type, object_name, object_size))

            elif db_type == 'postgresql':
                conn_source = psycopg2.connect(dbname=database, user=user, password=password, host=host, port="5432")
                conn_source.set_session(autocommit=True)
                cur1 = conn_source.cursor(cursor_factory=psycopg2.extras.DictCursor)

                sql_query = {
                    'Database': "SELECT current_database() AS object_database;",
                    'Table': "SELECT TABLE_SCHEMA AS object_schema, TABLE_NAME AS object_name, 'Table' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';",
                    'View': "SELECT TABLE_SCHEMA AS object_schema, TABLE_NAME AS object_name, 'View' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.VIEWS;",
                    'Function': "SELECT ROUTINE_SCHEMA AS object_schema, ROUTINE_NAME AS object_name, 'Function' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE = 'FUNCTION';",
                    'Stored_Procedure': "SELECT ROUTINE_SCHEMA AS object_schema, ROUTINE_NAME AS object_name, 'Stored_Procedure' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE = 'PROCEDURE';",
                    'Trigger': "SELECT TRIGGER_SCHEMA AS object_schema, TRIGGER_NAME AS object_name, 'Trigger' AS object_type, 'Unknown size' AS size FROM INFORMATION_SCHEMA.TRIGGERS;",
                    'Index': "SELECT schemaname AS object_schema, indexname AS object_name, 'Index' AS object_type, 'Unknown size' AS size FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog', 'information_schema');"
                }

                for query_type, query in sql_query.items():
                    cur1.execute(query)
                    for row in cur1.fetchall():
                        object_database = database
                        object_schema_name = row.get('object_schema')
                        object_name = row.get('object_name')
                        object_type = row.get('object_type')
                        object_size = row.get('size', 'Unknown size')
                        print(row)
                        if object_name is not None and \
                                (object_database, object_schema_name, object_type, object_name, object_size) not in existing_records:
                            insert_sql = """
                                            INSERT INTO metadata (object_database, object_schema, object_type, object_name, object_size) 
                                            VALUES (%s, %s, %s, %s, %s)
                                        """
                            cur.execute(insert_sql, (object_database, object_schema_name, object_type, object_name, object_size))
                            existing_records.append((object_database, object_schema_name, object_type, object_name, object_size))

            else:
                print("Unsupported database type:", db_type)

            # Commit the transaction after all records are processe

                conn_pg.commit()
                return HttpResponse("Data migration successful!")

        except Exception as e:
            conn_pg.rollback()
            return HttpResponse(f"Error occurred while scanning and storing data: {e}")

        finally:
            cur.close()
            conn_pg.close()

    return redirect("data_catalogue")

def user_logs(username, database_name, access_granted):
    conn_pg = connect_to_postgresql()
    cur = conn_pg.cursor()
    
    try:
        # Insert user log into PostgreSQL table
        cur.execute("INSERT INTO user_log (user_name, database_name, access_granted) VALUES (%s, %s, %s);", (username, database_name, access_granted))
        
        # Commit changes and close connection
        conn_pg.commit()
        cur.close()
        conn_pg.close()
    except Exception as e:
        # Handle any errors in logging
        print(f"Error logging user access: {e}")
        conn_pg.rollback()
        cur.close()
        conn_pg.close()

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.method == "POST":
        db_type = request.POST.get('db_type')
        host = request.POST.get('host')
        user = request.POST.get('user')
        password = request.POST.get('password')

        print("=================================")
        # print(target_db_type)
        print(db_type)
        # print(database)
        print(password)
        print(user)
        print(host)

        print("===================")

        # print(db_type, host, user, password)

        print("====================")



        access_granted, connection, db_names = get_db_connection(db_type, host, user, password)

        print(db_names)
        if access_granted:
            # connection.close()
            return render(request, 'migrationapp/data_mig.html', {'db_names': db_names})
        else:
            return render(request, 'migrationapp/data_mig.html', {'error_message': "Invalid database credentials. Please try again."})

    return render(request, 'migrationapp/dashboard.html')

def get_database_name(request):
    if request.method == 'POST':
        # form = MyForm(request.POST)
        # if form.is_valid():
        selected_value = request.POST.get('db_type')
        return selected_value
    return render(request, 'data_mig.html')

def data_mig(request):
    if request.method == "POST":
        target_db_type = request.POST.get('target_db_type')
        host = request.POST.get('db_server')
        user = request.POST.get('db_username')
        password = request.POST.get('db_password')
        db_type = request.POST.get('db_type')

        database = get_database_name()



        print("=======get_database_name======database: ", database)



        conn_source = connect_to_source_database(target_db_type, host, user, password, database)

        if conn_source is not None:
            success = scan_and_store_data(request, conn_source, target_db_type, db_type, database, password, user, host)
            if success:
                return render(request, 'migrationapp/data_catalogue.html')
            else:
                return render(request, 'migrationapp/data_mig.html', {'db_names': db_names})
        else:
            return HttpResponse("Error: Connection to source database failed!")

    return render(request, 'migrationapp/data_catalogue.html')

def get_db_connection(db_type, host, user, password):
    # Initialize variables
    connection = None
    access_granted = False
    db_names = []

    try:
        # Attempt database connection based on the selected type
        if db_type == 'mysql':
            connection = mysql.connector.connect(host=host, user=user, password=password)
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SHOW DATABASES")
                db_names = [db[0] for db in cursor.fetchall()]
                cursor.close()
                access_granted = True
        elif db_type == 'postgresql':
            print(host)
            connection = psycopg2.connect(host=host, user=user, password=password, port='5432')
            if connection is not None:
                cursor = connection.cursor()
                cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                db_names = [db[0] for db in cursor.fetchall()]
                cursor.close()
                access_granted = True
        elif db_type == 'sqlserver':
            connection = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=' + host + ';'
                'UID=' + user + ';'
                'PWD=' + password
            )
            if connection is not None:
                cursor = connection.cursor()
                cursor.execute("SELECT name FROM sys.databases")
                db_names = [db[0] for db in cursor.fetchall()]
                cursor.close()
                access_granted = True
    except Exception as e:
        print("Error:", e)
    return access_granted, connection, db_names

def connect_to_source_database(db_type, host, user, password, database):
    # Connect to the source database based on the type
    conn_source = None
    try:
        if db_type == 'postgresql':
            conn_source = psycopg2.connect(dbname=database, user=user, password=password, host=host, port='5432')
        elif db_type == 'mysql':
            conn_source = mysql.connector.connect(host=host, user=user, password=password, database=database)
        elif db_type == 'sqlserver':
            conn_source = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=' + host + ';'
                'UID=' + user + ';'
                'PWD=' + password
            )
    except Exception as e:
        print("Error connecting to database:", str(e))
    
    return conn_source
