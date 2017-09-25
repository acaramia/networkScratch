import pymysql.cursors

class Db:

    connection = None

    """

    Database: scratchserver
    Nome utente: scratch
    myscracth
    Email: comodo3141@gmail.com

    https://github.com/PyMySQL/PyMySQL
    
    """

    def __init__(self):
        # Connect to the database
        print("connecting to ip 85.10.205.173 for fast connection (real hostname is mysql8.db4free.net)")
        self.connection = pymysql.connect(host='85.10.205.173', #mysql8.db4free.net',
                                     port=3307,
                                     user='scratch',
                                     password='myscratch',
                                     db='scratchserver',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        print("ready")
        self.createtable()

    def drop(self):
        print("drop table")
        sql = "drop table vars"
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql)
            except:
                pass
            self.connection.commit()

    def createtable(self):
        print("create table (please ignore warning 1050, Table 'vars' already exists)")
        sql="""
        CREATE TABLE IF NOT EXISTS vars (
           
            username varchar(255) COLLATE utf8_bin,
            varname varchar(255) COLLATE utf8_bin,
            varvalue varchar(255) COLLATE utf8_bin,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (username,varname)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        """
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql)
            except:
                pass
            self.connection.commit()

    def insert(self,varname,varvalue,username):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO vars (varname, varvalue, username ) VALUES (%s, %s, %s) " \
                  "ON DUPLICATE KEY " \
                  "UPDATE varvalue = %s"
            cursor.execute(sql, (varname, varvalue, username, varvalue))
            self.connection.commit()

    def select(self,varname,username):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT varvalue FROM vars where varname=%s and username=%s"
            cursor.execute(sql,(varname,username))
            result = cursor.fetchone()
            if result and ("varvalue" in result):
                return result["varvalue"]
            else:
                return "{} of {} not found".format(varname,username)

    def disconnect(self):
        self.connection.close()


if __name__ == "__main__":
    c=Db()
    c.drop()
    c.createtable()
    c.insert('test1','www','u2')
    print(c.select('test1','u2'))
    c.disconnect()
