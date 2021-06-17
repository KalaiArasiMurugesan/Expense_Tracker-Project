import parser
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from PIL import ImageTk, Image
from pandas import DataFrame

from matplotlib.figure import Figure
from matplotlib import pyplot as plt


import os
import math
import sqlite3 as db

from tkcalendar import DateEntry

category = []
percentage = []

def init():
    connectionObjn = db.connect("expenseTracker.db")
    curr = connectionObjn.cursor()
    query = '''
    create table if not exists expenses (
        dateval datetime,
        month number,
        credit number,
        debit number,
        category string
        )
    '''
    curr.execute(query)
    connectionObjn.commit()


def clearhistory():
    connectionObjn = db.connect("expenseTracker.db")
    curr = connectionObjn.cursor()
    query = '''
     Delete FROM expenses
    '''
    curr.execute(query)
    connectionObjn.commit()


def refresh():
    root.destroy()
    os.popen("Project.py")


def submitexpense():
    date = dateEntry.get_date()
    values = [dateEntry.get(), date.strftime('%m'),Amount.get(), Category.get()]
    if(Category.get()=="Select category"):
        tkinter.messagebox.showinfo("Info", "Please select category")
    elif (Amount.get() == 0):
        tkinter.messagebox.showinfo("Info", "Amount should be gsreater than 0")
    else:
        connectionObjn = db.connect("expenseTracker.db")
        curr = connectionObjn.cursor()
        query = '''
        INSERT INTO EXPENSES VALUES 
        (?, ?, ?, ?, ?)
        '''
        if(Category.get() == "Income"):
            curr.execute(query, (dateEntry.get(), date.strftime('%m'), Amount.get(), 0, Category.get()))
        else:
            curr.execute(query, (dateEntry.get(), date.strftime('%m'), 0, Amount.get(), Category.get()))
        connectionObjn.commit()
        if(Category.get()=="Income"):
            msg = Category.get() + " added successfuly"
            tkinter.messagebox.showinfo("Info", msg)
        else:
            msg1 = Category.get() + " expense added successfuly"
            tkinter.messagebox.showinfo("Info", msg1)


        Month = StringVar()
        my_month = getallMonths()
        Month.set("Select Month")  # default value

        monthEntryMenu = OptionMenu(root, Month, *my_month, command=monthlyanalysis)
        monthEntryMenu.grid(row=5, column=1, padx=17, pady=7)
        monthEntryMenu.config(width=15)



def getexpensebycategory(cat,mon):
    sum=0
    connectionobjn = db.connect("expenseTracker.db")
    curr = connectionobjn.cursor()
    query = '''
      SELECT sum(debit) FROM EXPENSES WHERE category = ? AND month = ?
    '''
    curr.execute(query, (cat, mon))
    rows = curr.fetchall()
    print(cat, " - ", mon, " - ", rows)
    for row in rows:
        print(cat," - ",mon," - ",row[0])
        if (row[0] is not None):
            sum = row[0]
        else:
            sum = 0
    print(cat, " - ", mon, " - ", sum)
    return sum


def getallMonths(*args):
    connectionobjn = db.connect("expenseTracker.db")
    curr = connectionobjn.cursor()
    query = '''
      SELECT distinct month FROM EXPENSES 
    '''
    curr.execute(query)
    rows = curr.fetchall()
    monlist=[]
    for row in rows:
        if (row[0] is not None):
            monlist.append(row[0])
        else:
            monlist = ["No Records Found"]
    print(monlist)
    return monlist


def queryincome():
    income = 0
    connectionObjn = db.connect("expenseTracker.db")
    curr = connectionObjn.cursor()
    query = '''
         SELECT sum(credit) FROM EXPENSES WHERE category = ? AND month = ?
        '''
    print("Month.get()-", Month.get())
    curr.execute(query, ("Income", Month.get()))
    rows = curr.fetchall()

    for row in rows:
        if(row[0] is not None):
            income = row[0]
            break
    return income





def monthlyanalysis(*args):

        if(Month.get() == "No Records Found"):
            tkinter.messagebox.showinfo("Info", "No Records Found")
            raise ValueError("No Records Found")

        connectionObjn = db.connect("expenseTracker.db")
        curr = connectionObjn.cursor()
        query = '''
             SELECT category,debit,dateval FROM EXPENSES WHERE category <> ? AND month = ?
            '''
        curr.execute(query, ("Income", Month.get()))
        rows = curr.fetchall()

        monthyincome = queryincome()
        print("Income for",Month.get(), " - ", monthyincome)

        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                        font=('Calibri', 11))  # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))  # Modify the font of the headings
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        Elist = ['Category', 'Expense', 'Percentage', ]
        Etable = ttk.Treeview(root, column=Elist, show='headings', height=int(len(my_list) + 3), style="mystyle.Treeview")
        for c in Elist:
            Etable.heading(c, text=c.title())
        Etable.grid(row=6, column=0, padx=15, pady=7, columnspan=3)

        totalexp=0

        for cat in my_list:

            if (cat != "Income"):
                catexppercent=0
                catexp = int(getexpensebycategory(cat, Month.get()))
                print("catexp---",catexp)
                if(monthyincome != 0):
                    catexppercent = (catexp / monthyincome) * 100
                totalexp = totalexp + catexp

                values = [cat, str(catexp), str(round(catexppercent, 2))]
                Etable.insert('', 'end', values=values, tags=('Expense',))
                category.append(cat)
                percentage.append(str(round(catexppercent, 2)))

        if (monthyincome != 0):
            totalexppercent = (totalexp / monthyincome) * 100
        emptyvalues = ["", "", ""]
        Etable.insert('', 'end', values=emptyvalues)
        totvalues = ["TOTAL EXPENSES", totalexp, str(round(totalexppercent, 2)), 'Percent of your Income']
        Etable.insert('', 'end', values=totvalues, tags=('Total',))
        Etable.tag_configure('Total', font='#3776ab')

        """plt.bar(category, percentage)
        plt.show()

        y = np.array(percentage)
        plt.pie(y, labels=category , autopct=percentage[], shadow = True)
        plt.show()"""


init()
root = Tk()
root.title("My Expense Tracker")
root.geometry('1000x600')
root.state('zoomed')
root['background'] = '#EE82EE'
root.wm_iconbitmap('pen.ico')
root.wm_title('My Expense Tracker')

dateLabel = Label(root, text="Date", font=('arial', 15, 'bold'),bg="violet", fg="black", width=12)
dateLabel.grid(row=0, column=0, padx=7, pady=7)

dateEntry = DateEntry(root, width=12, font=('arial', 15, 'bold'))
dateEntry.grid(row=0, column=1, padx=7, pady=7)

Amount = IntVar()
expenseLabel = Label(root, text="Amount", font=('arial', 15, 'bold'),bg="violet", fg="black", width=12)
expenseLabel.grid(row=1, column=0, padx=7, pady=7)

expenseEntry = Entry(root, textvariable=Amount, font=('arial', 15, 'bold'))
expenseEntry.grid(row=1, column=1, padx=7, pady=7)

Category = StringVar()
my_list = ["Income","Travel","Food","Hobbies","Education","Bills","Misc"]
Category.set("Select category") # default value

catEntry = Label(root, text="Category", font=('arial', 15, 'bold'),bg="violet", fg="black", width=12)
catEntry.grid_configure( row=2, column=0, padx=7, pady=7)

catEntryMenu = OptionMenu(root, Category, *my_list)
catEntryMenu.grid(row=2, column=1, padx=17, pady=7)
catEntryMenu.config(width=30)

ExpenseAnalysis = Label(root, text="Expense Analyser", font=('arial', 15, 'bold'), bg="violet", fg="black", width=15)
ExpenseAnalysis.grid(row=5, column=0, padx=20, pady=7)


submitbtn = Button(root, command=submitexpense, text="Submit", font=('arial', 15, 'bold',), fg="black", bg="white",
                   width=12)
submitbtn.grid(row=4, column=1, padx=13, pady=13)



Month = StringVar()
my_month = getallMonths()
Month.set("Select Month")# default value

monthEntryMenu = OptionMenu(root, Month, *my_month, command=monthlyanalysis)
monthEntryMenu.grid(row=5, column=1, padx=17, pady=7)
monthEntryMenu.config(width=15)

clearhis = Button(root, command=clearhistory, text="Clear History", font=('arial', 15, 'bold'), bg="white",
                fg="black", width=12)
clearhis.grid(row=4, column=3, padx=2, pady=2)

reload = Button(root, command=refresh, text="Reload", font=('arial', 15, 'bold'), bg="white",
                fg="black", width=12)
reload.grid(row=4, column=0, padx=1, pady=1)


mainloop()