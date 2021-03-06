from sqlite3 import *

class DBManager:
    def __init__(self, dbName):
        self.conn, self.cur = self.connect(dbName)


    def connect(self, dbName):
        try:
            dbConnection = connect(dbName)
            cursor       = dbConnection.cursor()

            return dbConnection , cursor

        except Error as error:
            print("Error while connecting to sqlite", error)


    def disconnect(self):
        self.cur.close()
        self.conn.close()
        

    def getTable(self, tableName):
        try:
            self.cur.execute("""SELECT * FROM """ + tableName)
            records = self.cur.fetchall()
            if records == []:
                return "The table is empty"
            return records

        except Error as error:
            print("Failed to read data from sqlite table", error)


    def addDF(self, tableName, lhs, rhs):
        try:
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            records = self.cur.fetchall()
            FuncDepExist = False
            for tables in records:
                if tables != [] and 'FuncDep' in tables:
                    FuncDepExist = True

            if FuncDepExist:
                print("FuncDep is detected in your database")
                self.cur.execute("INSERT INTO FuncDep (tableName, lhs, rhs) VALUES (?, ?, ?)" , (tableName, lhs, rhs))
                self.conn.commit()
                print("Your DF was successfully added to the dfTable in your database")

            else:
                print("creating a new FuncDep table in your database")
                self.cur.execute(f"CREATE TABLE FuncDep (tableName TEXT NOT NULL, lhs TEXT NOT NULL, rhs TEXT NOT NULL)")
                self.cur.execute("INSERT INTO FuncDep (tableName, lhs, rhs) VALUES (?,?,?)", (tableName, lhs, rhs))
                self.conn.commit()
                print("Your DF was successfully added to the new dfTable in your database")

        except Error as error :
            print("Failed to add your DF, syntax might be incorect please be sure to enter  : \n dfTableName \n tableName \n lhs1 lhs2 lhsn \n rhs")
        

    def deleteDF(self, tableName, lhs, rhs):
        try:
            self.cur.execute("SELECT * FROM FuncDep WHERE tableName=\'{0}\' AND lhs=\'{1}\' AND rhs=\'{2}\'".format(tableName, lhs, rhs))
            records = self.cur.fetchall()

            if records == []:
                raise exception("The DF you tried to remove does not exist, please try with other arguments")

            else:
                self.cur.execute("DELETE FROM FuncDep WHERE tableName=\'{0}\' AND lhs=\'{1}\' AND rhs=\'{2}\'".format(tableName, lhs, rhs))
                self.conn.commit()
                print("The DF was successfully deleted from the df table")

        except Error as error :
            print("The DB your entered does not exist.")

    def deleteAllDF(self, tableName):
        try:
            self.cur.execute("SELECT * FROM FuncDep WHERE tablename=\'{0}\'".format(tableName))
            records = self.cur.fetchall()
            
            if records == []:
                raise exception("There are no DF related to the table you entered to delete.")

            else:
                self.cur.execute("DELETE FROM FuncDep WHERE tableName=\'{0}\'".format(tableName))
                self.conn.commit()
                print("All the DF related to " + tableName + " were successfully deleted.")
        
        except Error as error:
            print("The DB you entered does not exist", error)

    def getAllDF(self, tableName):
        try:
            self.cur.execute("SELECT * FROM FuncDep WHERE tableName=\'{0}\'".format(tableName))
            records = self.cur.fetchall()

            return records

        except Error as error:
            print("Failed to read data from sqlite table", error)

    def displayDF(self, tableName): 
        records = self.getAllDF(tableName)
        result  = 0

        for DF in records : 
            if DF[0] == tableName:
                if not result:
                    result = "Here are all the DF(s) of the "+records[0][0]+ " table :\n"
                result += DF[1] + " -----> " + DF[2] + "\n"

        if not result:
            result = "No DF found for " + tableName

        print(result)

    def getAllTables(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = []
        for record in self.cur.fetchall():
            tables.append(record[0])
        return tables

    
    def searchKeys(self, tableName):
        attributs = []  # all attributes of the table (list of attributes)
        DF        = []  # all DF's of the table (list of tuples)
        DFleft    = []  # lhs
        DFright   = []  # rhs

        for df in self.getAllDF(tableName):  # get all lhs and rhs of the given table
            DFleft.append(df[1])
            DFright.append(df[2])
        
        # le pire algorithme du 21?? si??cle : delete all duplicates in the lists and keep the elements order
        tmp = []
        for l in DFleft:
            if l not in tmp:
                tmp.append(l)
        DFleft = tmp[:]

        tmp = []
        for r in DFright:
            if r not in tmp:
                tmp.append(r)
        DFright = tmp[:]

        columns  = self.cur.execute(f"PRAGMA table_info({tableName})") # puts all attributes of the table in the attributes list
        for c in columns.fetchall():
            attributs.append(c[1])
        DF = self.getAllDF(tableName)
        
        keys = []
        for a in attributs:         # puts attributes that are not in the DFright list in the keys list
            if a not in DFright:
                keys.append(a)
        keyLen = len(keys)
        pointer = 0

        for rhs in DFright:
            if rhs in keys:
                keys.remove(rhs)
        
        current = keys[0]
        while pointer < keyLen:
            if current in DFleft:
                keys.append(DFright[DFleft.index(current)])
                current = DFright[DFleft.index(current)]
            else :
                found = False
                for l in DFleft:
                    if current in l.split():
                        keys.append(DFright[DFleft.index(l)])
                        current = DFright[DFleft.index(l)]               
                        found = True
               
                if not found:
                    pointer += 1
                    current = keys[pointer]

        return ''.join(keys[:keyLen])
