import parser
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import os
import math
import sys
import sqlite3 as db

from tkcalendar import DateEntry

def init():    # Creation of Sqlite database titled "expenseTracker.db"
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




# submitexpense() is a method that receives user input and writes in the database.
def submitexpense():
    date = dateEntry.get_date()

    try:
        print(Amount.get())
        if (Amount.get() <= 0):
            raise ValueError("Please enter an valid amount")
        if (Category.get() == "Select category"):
            raise ValueError("Please select category")

    except ValueError as ve:
        tkinter.messagebox.showerror("Error", ve.args[0])
        raise
    except Exception as e:
        tkinter.messagebox.showerror("Error", "Please enter Amount")
        raise

    values = [dateEntry.get(), date.strftime('%m'), Amount.get(), Category.get()]
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
        popup_msg_for_income_category = Category.get() + " added successfully"
        tkinter.messagebox.showinfo("Info", popup_msg_for_income_category)
    else:
        popup_msg_for_expense_category= Category.get() + " expense added successfully"
        tkinter.messagebox.showinfo("Info", popup_msg_for_expense_category)



    my_month = getallMonths()
    Month.set("Select Month")  # default value

    monthEntryMenu = OptionMenu(root, Month, *my_month, command=monthlyanalysis)
    monthEntryMenu.grid(row=5, column=1, padx=17, pady=7)
    monthEntryMenu.config(width=15)

#1. getexpensebycategory is a method to calculate the sum of expenses for every category.
#2. The value returned by this method is passed as input to the monthlyanalysis method.
#3. cat is a variable that refers to the category and mon is a variable that refers to the chosen month.
#4. total_expense variable to calculate total expense per category.

def getexpensebycategory(cat,mon):
    total_expense = 0
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
            total_expense = row[0]
        else:
            total_expense = 0
    print(cat, " - ", mon, " - ", total_expense)
    return total_expense

#1. getallMonths is a method to display all the months for which expenses were recorded.
#2. The drop down in the GUI lists only those months for which the expenses were submitted.
#3. The value returned by this method is passed as input to the monthlyanalysis method.
#4. monlist[]An empty list declaration that will get populated with all the months for which records are present.

def getallMonths(*args):
    connectionobjn = db.connect("expenseTracker.db")
    curr = connectionobjn.cursor()
    query = '''
      SELECT distinct month FROM EXPENSES 
    '''
    curr.execute(query)
    rows = curr.fetchall()
    monlist=[]
    if len(rows) == 0:
        monlist = ["No Records Found"]

    for row in rows:
        if (row[0] is not None):
            monlist.append(row[0])
        else:
            monlist = ["No Records Found"]
    print(monlist)
    return monlist

#queryincome() method calculates the total income for the chosen month.
#The value returned by this method is passed as input to the monthlyanalysis method.

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


#1. monthlyanalyis method does the analysis of expenses based on values returned from getexpensebycategory(),getallMonths() and queryincome().
#2. totalexp is the variable to calculate the total expenses of the chosen month.
#3. catexp is the variable to calculate the total expenses per category .
#4. catexppercent is the variable to calculate the percentage of expenses per category


def monthlyanalysis(*args):

        if(Month.get() == "No Records Found"):
            tkinter.messagebox.showinfo("Info", "No Records Found, please add expenses")
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

        Elist = ['Category', 'Expense', 'Percentage on Income']
        Etable = ttk.Treeview(root, column=Elist, show='headings', height=int(len(my_list) + 3), style="mystyle.Treeview")
        for c in Elist:
            Etable.heading(c, text=c.title())
        Etable.grid(row=6, column=0, padx=15, pady=7, columnspan=3)
        totalexp=0
        totalexppercent = 0

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


        if (monthyincome != 0):
            totalexppercent = (totalexp / monthyincome) * 100
        emptyvalues = ["", "", ""]

        Etable.insert('', 'end', values=emptyvalues)
        totvalues = ["TOTAL EXPENSES", totalexp, str(round(totalexppercent, 2)), 'Percent of your Income']
        Etable.insert('', 'end', values=totvalues, tags=('Total',))
        Etable.tag_configure('Total', font='#3776ab')

        totincome = ["TOTAL INCOME", queryincome()]
        Etable.insert('', 'end', values=totincome, tags=('Total',))
        Etable.tag_configure('Total', font='#3776ab')

#clearhistory is a method to delete the records in the database

def clearhistory():
    answer = tkinter.messagebox.askyesno("Question", "Are you sure you want to erase all the previous records ?")
    if answer:
        connectionObjn = db.connect("expenseTracker.db")
        curr = connectionObjn.cursor()
        query = '''
         Delete FROM expenses
        '''
        curr.execute(query)
        connectionObjn.commit()
        popup_msg_after_deleting = "Previous records deleted"
        tkinter.messagebox.showinfo("Info", popup_msg_after_deleting)

        my_month = getallMonths()
        Month.set("Select Month")  # default value

        monthEntryMenu = OptionMenu(root, Month, *my_month, command=monthlyanalysis)
        monthEntryMenu.grid(row=5, column=1, padx=17, pady=7)
        monthEntryMenu.config(width=15)
    else:
        tkinter.messagebox.showinfo("Info", "Ok")

#refresh() method clears the contents of the screen and reloads a fresh page
def refresh():
    root.destroy()
    os.system(sys.argv[0])



# Start of main
init()
root = Tk()  # tkinter object declaration
root.title("My Expense Tracker")
root.geometry('1000x600')
root.state('zoomed')
root['background'] = 'violet'
root.wm_iconbitmap('pen.ico')
root.wm_title('My Expense Tracker')

# UI Design and Definition starts from here

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
Month.set("Select Month")
monthEntryMenu = OptionMenu(root, Month, *my_month, command=monthlyanalysis)
monthEntryMenu.grid(row=5, column=1, padx=17, pady=7)
monthEntryMenu.config(width=15)

clearhis = Button(root, command=clearhistory, text="Clear History", font=('arial', 15, 'bold'), bg="white",
                fg="black", width=12)
clearhis.grid(row=4, column=0, padx=2, pady=2)

reload = Button(root, command=refresh, text="Refresh", font=('arial', 15, 'bold'), bg="white",
                fg="black", width=12)
reload.grid(row=4, column=3, padx=1, pady=1)
mainloop()
