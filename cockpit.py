import mysql.connector
import tkinter as tk
from tkinter import *

my_connect=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="attendancesystem"
)
my_cursor=my_connect.cursor()

my_w=tk.Tk()
my_w.geometry=("400x200")
l1=tk.Label(my_w, text='Enter User ID: ',width=25)
l1.grid(row=1,column=1)
t1=tk.Text(my_w, height=1,width=4,bg='yellow')
t1.grid(row=1,column=2)

b1 = tk.Button(my_w, text='Show Details', width=15,bg='red',
    command=lambda: my_details(t1.get('1.0',END)))
b1.grid(row=1,column=4) 

my_str1 = tk.StringVar()
l2 = tk.Label(my_w,  textvariable=my_str1, width=30,fg='red' )  
l2.grid(row=3,column=1,columnspan=2) 
my_str1.set("Output USER database")

my_str2 = tk.StringVar()
l3 = tk.Label(my_w,  textvariable=my_str2, width=30,fg='red' )  
l3.grid(row=4,column=1,columnspan=2) 
my_str2.set("Output USER database")

my_str3 = tk.StringVar()
l4 = tk.Label(my_w,  textvariable=my_str3, width=30,fg='red' )  
l4.grid(row=5,column=1,columnspan=2) 
my_str3.set("Output ATTENDANCE database")

def my_details(id):
    try:
        val = int(id) # check input is integer or not
        try:
            my_cursor.execute("SELECT * FROM users WHERE id="+id)
            student = my_cursor.fetchone()
            my_str1.set("NOM : "+student[1])
            my_str2.set("N_TAG : "+str(student[2]))
            my_cursor.execute("SELECT user_id, COUNT(user_id) FROM attendance WHERE user_id="+id)
            nb_passage = my_cursor.fetchone()            
            my_str3.set("N_PASSAGE : "+str(nb_passage[1]))
        except : 
             my_str1.set("Database error")
             my_str2.set("Database error")
             my_str3.set("Database error")
    except:
        my_str1.set("Check input")
        my_str2.set("Check input")
my_w.mainloop()
