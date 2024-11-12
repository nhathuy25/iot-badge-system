import mysql.connector

db=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="attendancesystem"
)
print('CONSULTATION BDD UTILISATEURS')   
cursor=db.cursor()
cursor.execute("SELECT * FROM users")
for ligne in cursor.fetchall():
    print(ligne)
print('\n')
# print('CONSULTATION BDD TRACKING')  
# cursor.execute("SELECT * FROM attendance")
# for ligne in cursor.fetchall():
    # print(ligne)
db.close()
