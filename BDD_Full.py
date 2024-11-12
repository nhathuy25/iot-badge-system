import mysql.connector

db=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="attendancesystem"
)
print('CONSULTATION BDD UTILISATEURS')   
cursor=db.cursor()
cursor.execute("Select * from attendance")
for ligne in cursor.fetchall():
    print(ligne)
print('\n')
print('NOMBRE DE PASSAGES')  
cursor.execute("SELECT user_id, COUNT(user_id) FROM attendance GROUP BY user_id")
for ligne in cursor.fetchall():
    print(ligne)
print('\n')
# print('CONSULTATION BDD TRACKING')  
# cursor.execute("SELECT * FROM attendance")
# for ligne in cursor.fetchall():
    # print(ligne)
db.close()
