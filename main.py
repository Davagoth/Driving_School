from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from functools import partial
import tkinter.messagebox as tkMessageBox
import sqlite3
import datetime
import re
import pandas as pd

root = Tk()
root.title("Python: System Supporting the Management of a Driving Improvement School")

width = 650
height = 650
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))
root.resizable(0, 0)

MainFrame = None


def Database():
    global conn, cursor
    conn = sqlite3.connect("driving_school.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `user` (mem_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT, firstname TEXT, lastname TEXT, role TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `payment` (payment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, student_id INTEGER, what_for TEXT, amount REAL, payment_date TEXT, FOREIGN KEY(student_id) REFERENCES user(mem_id))")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `class_plan` (class_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, student_id INTEGER, instructor_id INTEGER, instructor_name TEXT, class_datetime TEXT, status TEXT, displayed INTEGER, FOREIGN KEY(instructor_id) REFERENCES user(mem_id))")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `rating` (rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, rating INTEGER, feedback TEXT, instructor_first_name TEXT, instructor_last_name TEXT)")

    cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'Admin'")
    result = cursor.fetchone()[0]

    if result == 0:
        cursor.execute(
            "INSERT INTO user (username, password, firstname, lastname, role) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin", "Admin", "Admin", "Admin")
        )
        conn.commit()


# =======================================VARIABLES=====================================
USERNAME = StringVar()
PASSWORD = StringVar()
FIRSTNAME = StringVar()
LASTNAME = StringVar()
ROLE = StringVar()
CONFIRM_PASSWORD = StringVar()
FEEDBACK = StringVar()


def LoginForm():
    global LoginFrame, lbl_result1, btn_login
    LoginFrame = Frame(root)
    LoginFrame.pack(side=TOP, pady=80)
    lbl_username = Label(LoginFrame, text="Username:", font=('arial', 25), bd=18)
    lbl_username.grid(row=1)
    lbl_password = Label(LoginFrame, text="Password:", font=('arial', 25), bd=18)
    lbl_password.grid(row=2)
    lbl_result1 = Label(LoginFrame, text="", font=('arial', 18))
    lbl_result1.grid(row=3, columnspan=2)
    username = Entry(LoginFrame, font=('arial', 20), textvariable=USERNAME, width=15)
    username.grid(row=1, column=1)
    password = Entry(LoginFrame, font=('arial', 20), textvariable=PASSWORD, width=15, show="*")
    password.grid(row=2, column=1)
    btn_login = Button(LoginFrame, text="Login", font=('arial', 18), width=35, command=Login)
    btn_login.grid(row=4, columnspan=2, pady=20)
    lbl_register = Label(LoginFrame, text="Register", fg="Blue", font=('arial', 12))
    lbl_register.grid(row=0, sticky=W)
    lbl_register.bind('<Button-1>', ToggleToRegister)


RegisterFrame = None


def RegisterForm():
    global RegisterFrame, lbl_result2
    RegisterFrame = Frame(root)
    RegisterFrame.pack(side=TOP, pady=40, anchor='center')

    lbl_username = Label(RegisterFrame, text="Username:", font=('arial', 18), bd=18)
    lbl_username.grid(row=1)
    lbl_password = Label(RegisterFrame, text="Password:", font=('arial', 18), bd=18)
    lbl_password.grid(row=2)
    lbl_confirm_password = Label(RegisterFrame, text="Confirm Password:", font=('arial', 18), bd=18)
    lbl_confirm_password.grid(row=3)
    lbl_name = Label(RegisterFrame, text="Name:", font=('arial', 18), bd=18)
    lbl_name.grid(row=4)
    lbl_surname = Label(RegisterFrame, text="Surname:", font=('arial', 18), bd=18)
    lbl_surname.grid(row=5)

    username = Entry(RegisterFrame, font=('arial', 20), textvariable=USERNAME, width=15)
    username.grid(row=1, column=1)
    password = Entry(RegisterFrame, font=('arial', 20), textvariable=PASSWORD, width=15, show="*")
    password.grid(row=2, column=1)
    confirm_password = Entry(RegisterFrame, font=('arial', 20), textvariable=CONFIRM_PASSWORD, width=15, show="*")
    confirm_password.grid(row=3, column=1)
    name = Entry(RegisterFrame, font=('arial', 20), textvariable=FIRSTNAME, width=15)
    name.grid(row=4, column=1)
    surname = Entry(RegisterFrame, font=('arial', 20), textvariable=LASTNAME, width=15)
    surname.grid(row=5, column=1)

    lbl_role = Label(RegisterFrame, text="Role:", font=('arial', 18), bd=18)
    lbl_role.grid(row=6)
    role_choices = ['Student', 'Instructor']
    rolee = ttk.Combobox(RegisterFrame, values=role_choices, textvariable=ROLE, font=('arial', 20), state='readonly')
    rolee.current(0)
    rolee.grid(row=6, column=1)

    lbl_result2 = Label(RegisterFrame, text="", font=('arial', 18))
    lbl_result2.grid(row=9, columnspan=2)

    btn_register = Button(RegisterFrame, text="Register", font=('arial', 18), width=35, command=Register)
    btn_register.grid(row=7, columnspan=2, pady=20)

    lbl_login = Label(RegisterFrame, text="Already registered? Click Login!", fg="Blue", font=('arial', 14))
    lbl_login.grid(row=8, columnspan=2, pady=(0, 20), sticky='n')
    lbl_login.bind('<Button-1>', ToggleToLogin)

    RegisterFrame.pack()


def InstructorForm():
    global MainFrame
    MainFrame = Frame(root)
    MainFrame.pack(side=TOP, pady=40)

    lbl_logout = Label(MainFrame, text="Logout", fg="Blue", font=('arial', 12))
    lbl_logout.grid(row=0, column=1, sticky=NE)
    lbl_logout.bind('<Button-1>', lambda event: Logout())

    btn_manage_classes = Button(MainFrame, text="Manage Classes", font=('arial', 18), width=35, command=manage_classes)
    btn_manage_classes.grid(row=2, pady=10)

    btn_view_classes = Button(MainFrame, text="View Classes", font=('arial', 18), width=35, command=view_classes)
    btn_view_classes.grid(row=3, pady=10)

    check_new_entries(0)


def MainForm():
    global MainFrame
    MainFrame = Frame(root)
    MainFrame.pack(side=TOP, pady=40)

    lbl_logout = Label(MainFrame, text="Logout", fg="Blue", font=('arial', 12))
    lbl_logout.grid(row=0, column=1, sticky=NE)
    lbl_logout.bind('<Button-1>', lambda event: Logout())

    btn_plan_classes = Button(MainFrame, text="Propose Term", font=('arial', 18), width=35, command=plan_classes)
    btn_plan_classes.grid(row=2, pady=10)

    btn_enter_payment = Button(MainFrame, text="Enter Payment", font=('arial', 18), width=35, command=enter_payment)
    btn_enter_payment.grid(row=3, pady=10)

    btn_rate = Button(MainFrame, text="Rate", font=('arial', 18), width=35, command=rate)
    btn_rate.grid(row=4, pady=10)

    btn_view_classes = Button(MainFrame, text="View Classes", font=('arial', 18), width=35, command=view_classes)
    btn_view_classes.grid(row=5, pady=10)

    check_new_entries(1)


def check_new_entries(number):
    if number == 0:
        try:
            cursor.execute(
                "SELECT class_id, student_id, class_datetime FROM class_plan WHERE status = 'Proposed' AND displayed = 0"
            )
            new_entries = cursor.fetchall()

            for entry in new_entries:
                class_id = entry[0]
                student_id = entry[1]
                class_datetime = entry[2]

                cursor.execute(
                    "SELECT firstname, lastname FROM user WHERE mem_id = ?",
                    (student_id,)
                )
                student_name = cursor.fetchone()

                messagebox.showinfo("New Proposal",
                                    f"You have received a new term proposal from {student_name[0]} {student_name[1]} for the date and time: {class_datetime}. Please review and accept/reject accordingly.")

                cursor.execute(
                    "UPDATE class_plan SET displayed = 1 WHERE class_id = ?",
                    (class_id,)
                )
                conn.commit()

        except Exception as e:
            print("Error checking for new entries:", e)

    else:
        try:
            cursor.execute(
                "SELECT class_id, instructor_id, class_datetime, status FROM class_plan WHERE (status = 'Scheduled' OR status = 'Rejected') AND displayed = 1"
            )
            new_entries = cursor.fetchall()

            for entry in new_entries:
                class_id = entry[0]
                instructor_id = entry[1]
                class_datetime = entry[2]
                status = entry[3]

                cursor.execute(
                    "SELECT firstname, lastname FROM user WHERE mem_id = ?",
                    (instructor_id,)
                )
                instructor_name = cursor.fetchone()

                if status == 'Scheduled':
                    messagebox.showinfo("New Message",
                                        f"Instructor {instructor_name[0]} {instructor_name[1]} has accepted your proposed date: {class_datetime}.")
                elif status == 'Rejected':
                    messagebox.showinfo("New Message",
                                        f"Instructor {instructor_name[0]} {instructor_name[1]} has rejected your proposed date: {class_datetime}.")

                cursor.execute(
                    "UPDATE class_plan SET displayed = 2 WHERE class_id = ?",
                    (class_id,)
                )
                conn.commit()

        except Exception as e:
            print("Error checking for new entries:", e)


def AdminForm():
    global MainFrame
    MainFrame = Frame(root)
    MainFrame.pack(side=TOP, pady=40)

    lbl_logout = Label(MainFrame, text="Logout", fg="Blue", font=('arial', 12))
    lbl_logout.grid(row=0, column=1, sticky=NE)
    lbl_logout.bind('<Button-1>', lambda event: Logout())

    btn_view_classes = Button(MainFrame, text="View Classes", font=('arial', 18), width=35, command=view_classes)
    btn_view_classes.grid(row=1, pady=10)

    btn_report_analyze = Button(MainFrame, text="Report and Analyze", font=('arial', 18), width=35,
                                command=report_analyze_progress)
    btn_report_analyze.grid(row=2, pady=10)


# =======================================METHODS=======================================
def Exit():
    result = tkMessageBox.askquestion('System', 'Are you sure you want to exit?', icon="warning")
    if result == 'yes':
        root.destroy()
        exit()


def ToggleToLogin(event=None):
    RegisterFrame.destroy()
    LoginForm()


def ToggleToRegister(event=None):
    LoginFrame.destroy()
    RegisterForm()


def ToggleToMain(event=None):
    LoginFrame.destroy()
    if USERNAME.get() == "admin" and PASSWORD.get() == "admin":
        AdminForm()
    else:
        cursor.execute("SELECT * FROM `user` WHERE `username` = ? and `password` = ?",
                       (USERNAME.get(), PASSWORD.get()))
        user = cursor.fetchone()
        if user is not None:
            rolee = user[5]
            if rolee == "Instructor":
                InstructorForm()
            else:
                MainForm()
        else:
            lbl_result1.config(text="Invalid Username or Password", fg="red")


def Register():
    Database()
    if USERNAME.get() == "" or PASSWORD.get() == "" or FIRSTNAME.get() == "" or LASTNAME.get() == "" or CONFIRM_PASSWORD.get() == "":
        lbl_result2.config(text="Please complete all the required fields!", fg="orange")
    elif not FIRSTNAME.get().isalpha() or not LASTNAME.get().isalpha():
        lbl_result2.config(text="Name and surname should contain only letters!", fg="red")
    elif not FIRSTNAME.get().istitle() or not LASTNAME.get().istitle():
        lbl_result2.config(text="Name and surname should start with a capital letter!", fg="red")
    elif not PASSWORD.get() == CONFIRM_PASSWORD.get():
        lbl_result2.config(text="Passwords don't match!", fg="red")
    else:
        cursor.execute("SELECT * FROM `user` WHERE `username` = ?", (USERNAME.get(),))
        if cursor.fetchone() is not None:
            lbl_result2.config(text="Username is already taken", fg="red")
        else:
            cursor.execute("INSERT INTO `user` (username, password, firstname, lastname, role) VALUES (?, ?, ?, ?, ?)",
                           (str(USERNAME.get()), str(PASSWORD.get()), str(FIRSTNAME.get()), str(LASTNAME.get()),
                            str(ROLE.get())))
            conn.commit()
            USERNAME.set("")
            PASSWORD.set("")
            FIRSTNAME.set("")
            LASTNAME.set("")
            CONFIRM_PASSWORD.set("")
            lbl_result2.config(text="Successfully Created!", fg="black")
            root.after(5000, partial(ToggleToLogin))
        cursor.close()
        conn.close()


def Login():
    Database()
    if USERNAME.get() == "" or PASSWORD.get() == "":
        lbl_result1.config(text="Please complete the required field!", fg="orange")
    else:
        cursor.execute("SELECT * FROM `user` WHERE `username` = ? and `password` = ?",
                       (USERNAME.get(), PASSWORD.get()))
        if cursor.fetchone() is not None:
            lbl_result1.config(text="Successfully logged in!", fg="green")
            btn_login.config(state=DISABLED)
            root.after(5000, partial(ToggleToMain))
        else:
            lbl_result1.config(text="Invalid Username or Password", fg="red")


def Logout():
    MainFrame.destroy()
    root.deiconify()
    LoginForm()
    USERNAME.set("")
    PASSWORD.set("")


def enter_payment():
    global lbl_result
    payment_window = Toplevel(root)
    payment_window.title("Enter Payment")

    cursor.execute("SELECT mem_id FROM `user` WHERE `username` = ?", (USERNAME.get(),))
    user_id = cursor.fetchone()[0]

    lbl_payment_for = Label(payment_window, text="Payment For:")
    lbl_payment_for.pack()
    payment_for_var = StringVar(payment_window)
    payment_for_var.set("Class Payment")
    payment_for_dropdown = OptionMenu(payment_window, payment_for_var, "Class Payment", "Other Payment")
    payment_for_dropdown.pack()

    lbl_amount = Label(payment_window, text="Amount to Pay:")
    lbl_amount.pack()
    amount_var = StringVar(payment_window)
    amount_var.set("10")
    amount_dropdown = OptionMenu(payment_window, amount_var, "10", "20", "50", "100")
    amount_dropdown.pack()

    lbl_result = Label(payment_window, text="", fg="red")
    lbl_result.pack()

    def select_payment():
        payment_option = payment_for_var.get()
        payment_amount = amount_var.get()

        payment_window.destroy()
        payment_screen(payment_option, payment_amount)

    def payment_screen(payment_option, payment_amount):
        pay_screen = Toplevel(root)
        pay_screen.title("Payment Screen")

        lbl_form_payment = Label(pay_screen, text="Form of Payment:")
        lbl_form_payment.pack()
        form_payment_var = StringVar(pay_screen)
        form_payment_var.set("Credit Card")
        form_payment_dropdown = OptionMenu(pay_screen, form_payment_var, "Credit Card", "PayPal", "BLIK")
        form_payment_dropdown.pack()

        def submit_payment():
            selected_payment = form_payment_var.get()
            pay_screen.destroy()
            if selected_payment == "Credit Card":
                credit_card_screen(payment_option, payment_amount)
            elif selected_payment == "PayPal":
                paypal_screen(payment_option, payment_amount)
            elif selected_payment == "BLIK":
                blik_screen(payment_option, payment_amount)

        btn_submit_payment = Button(pay_screen, text="Submit Payment", command=lambda: submit_payment())
        btn_submit_payment.pack()

    def credit_card_screen(payment_option, payment_amount):
        cc_screen = Toplevel(root)
        cc_screen.title("Credit Card Payment")

        lbl_cc_number = Label(cc_screen, text="Card Number (16 digits):")
        lbl_cc_number.pack()
        entry_cc_number = Entry(cc_screen)
        entry_cc_number.pack()

        lbl_cc_cvc = Label(cc_screen, text="CVC (3 digits):")
        lbl_cc_cvc.pack()
        entry_cc_cvc = Entry(cc_screen)
        entry_cc_cvc.pack()

        def validate_credit_card_data(cc_number, cc_cvc):
            if len(cc_number) != 16 or not cc_number.isdigit():
                return False
            if len(cc_cvc) != 3 or not cc_cvc.isdigit():
                return False
            return True

        def submit_credit_card_payment():
            cc_number = entry_cc_number.get().strip()
            cc_cvc = entry_cc_cvc.get().strip()

            if not validate_credit_card_data(cc_number, cc_cvc):
                lbl_resu = Label(cc_screen, text="Invalid credit card data.", fg="red")
                lbl_resu.place(relx=0.5, rely=0.5, anchor=CENTER)
                cc_screen.update_idletasks()
                cc_screen.after(2000, lambda: lbl_resu.config(text=""))
            else:
                cc_screen.destroy()
                summary_screen(payment_option, "Credit Card", payment_amount, cc_number, cc_cvc)

        btn_submit_cc_payment = Button(cc_screen, text="Submit Payment", command=submit_credit_card_payment)
        btn_submit_cc_payment.pack()

    def paypal_screen(payment_option, payment_amount):
        pypl_screen = Toplevel(root)
        pypl_screen.title("PayPal Payment")

        lbl_paypal_user = Label(pypl_screen, text="PayPal Username:")
        lbl_paypal_user.pack()
        entry_paypal_user = Entry(pypl_screen)
        entry_paypal_user.pack()

        lbl_paypal_email = Label(pypl_screen, text="PayPal Email:")
        lbl_paypal_email.pack()
        entry_paypal_email = Entry(pypl_screen)
        entry_paypal_email.pack()

        def validate_paypal_data(email):
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return False
            return True

        def submit_paypal_payment():
            username = entry_paypal_user.get().strip()
            email = entry_paypal_email.get().strip()

            if not validate_paypal_data(email):
                lbl_resu = Label(pypl_screen, text="Invalid PayPal data.", fg="red")
                lbl_resu.place(relx=0.5, rely=0.5, anchor=CENTER)
                pypl_screen.update_idletasks()
                pypl_screen.after(2000, lambda: lbl_resu.config(text=""))
            else:
                pypl_screen.destroy()
                summary_screen(payment_option, "PayPal", payment_amount, username, email)

        btn_submit_paypal_payment = Button(pypl_screen, text="Submit Payment", command=submit_paypal_payment)
        btn_submit_paypal_payment.pack()

    def blik_screen(payment_option, payment_amount):
        blik_scrn = Toplevel(root)
        blik_scrn.title("BLIK Payment")

        lbl_blik_code = Label(blik_scrn, text="BLIK Code (6 digits):")
        lbl_blik_code.pack()
        entry_blik_code = Entry(blik_scrn)
        entry_blik_code.pack()

        def validate_blik_code(blik_code):
            if len(blik_code) != 6 or not blik_code.isdigit():
                return False
            return True

        def submit_blik_payment():
            blik_code = entry_blik_code.get().strip()

            if not validate_blik_code(blik_code):
                lbl_resu = Label(blik_scrn, text="Invalid BLIK code.", fg="red")
                lbl_resu.place(relx=0.5, rely=0.5, anchor=CENTER)
                blik_scrn.update_idletasks()
                blik_scrn.after(2000, lambda: lbl_resu.config(text=""))
            else:
                blik_scrn.destroy()
                summary_screen(payment_option, "BLIK", payment_amount, blik_code, "NONE")

        btn_submit_blik_payment = Button(blik_scrn, text="Submit Payment", command=submit_blik_payment)
        btn_submit_blik_payment.pack()

    def summary_screen(payment_option, form_payment, payment_amount, payment_data1, payment_data2):
        summ_screen = Toplevel(root)
        summ_screen.title("Summary Screen")

        lbl_summary = Label(summ_screen, text="Payment Summary")
        lbl_summary.pack()

        lbl_payment_option = Label(summ_screen, text="Payment Option: " + payment_option)
        lbl_payment_option.pack()

        lbl_form_payment = Label(summ_screen, text="Form of Payment: " + form_payment)
        lbl_form_payment.pack()

        lbl_payment_amount = Label(summ_screen, text="Amount to Pay: $" + payment_amount)
        lbl_payment_amount.pack()

        lbl_payment_data1 = Label(summ_screen, text="Payment Data 1: " + payment_data1)
        lbl_payment_data1.pack()

        lbl_payment_data2 = Label(summ_screen, text="Payment Data 2: " + payment_data2)
        lbl_payment_data2.pack()

        def accept_payment():
            try:
                payment_notification(True, payment_option)

            except ValueError:
                payment_notification(False, payment_option)
            summ_screen.destroy()

        def reject_payment():
            try:
                payment_notification(False, payment_option)

            except ValueError:
                payment_notification(True, payment_option)
            summ_screen.destroy()

        btn_accept_payment = Button(summ_screen, text="Accept Payment", command=accept_payment)
        btn_accept_payment.pack()

        btn_reject_payment = Button(summ_screen, text="Reject Payment", command=reject_payment)
        btn_reject_payment.pack()

    def payment_notification(successful, payment_option):
        notification_screen = Toplevel(root)
        notification_screen.title("Payment Notification")

        if successful:
            payment_amount = amount_var.get()
            if payment_amount:
                cursor.execute(
                    "INSERT INTO `payment` (student_id, what_for, amount, payment_date) VALUES (?, ?, ?, ?)",
                    (user_id, str(payment_option), str(payment_amount), str(datetime.datetime.now()))
                )
                conn.commit()
                lbl_notification = Label(notification_screen, text="Payment successful!")
                lbl_notification.pack()
            else:
                lbl_notification = Label(notification_screen, text="Payment unsuccessful. Amount is missing.")
                lbl_notification.pack()
        else:
            lbl_notification = Label(notification_screen, text="Payment unsuccessful.")
            lbl_notification.pack()

    btn_enter_payment = Button(payment_window, text="Enter Payment", command=select_payment)
    btn_enter_payment.pack()


def plan_classes():
    class_plan_window = Toplevel(root)
    class_plan_window.title("Propose Term")

    cursor.execute("SELECT mem_id FROM `user` WHERE `username` = ?", (USERNAME.get(),))
    user_id = cursor.fetchone()[0]

    entry_student_id = Entry(class_plan_window, state="readonly")
    entry_student_id.insert(END, user_id)

    lbl_instructor_name = Label(class_plan_window, text="Instructor Name:")
    lbl_instructor_name.pack()

    instructor_list = []
    cursor.execute("SELECT * FROM `user` WHERE `role` = 'Instructor'")
    instructors = cursor.fetchall()
    for instructor in instructors:
        instructor_list.append(instructor[3] + " " + instructor[4])

    instructor_var = StringVar(class_plan_window)
    instructor_var.set(instructor_list[0])

    instructor_dropdown = OptionMenu(class_plan_window, instructor_var, *instructor_list)
    instructor_dropdown.pack()

    lbl_class_datetime = Label(class_plan_window, text="Class Date and Time:")
    lbl_class_datetime.pack()

    entry_class_datetime = Entry(class_plan_window)
    entry_class_datetime.pack()

    cal = Calendar(class_plan_window, selectmode="day", date_pattern="yyyy-mm-dd", cursor="hand1")
    cal.pack()

    time_var = StringVar(class_plan_window)

    available_times = []
    start_time = datetime.datetime.strptime("09:00", "%H:%M")
    end_time = datetime.datetime.strptime("17:00", "%H:%M")
    delta = datetime.timedelta(minutes=30)
    current_time = start_time

    while current_time <= end_time:
        available_times.append(current_time.strftime("%H:%M"))
        current_time += delta

    time_var.set(available_times[0])

    time_dropdown = OptionMenu(class_plan_window, time_var, *available_times)
    time_dropdown.pack()

    def on_date_time_selected():
        selected_date = cal.selection_get()
        selected_time = time_var.get()
        current_datetime = datetime.datetime.now()
        if selected_date < current_datetime.date():
            lbl_rslt.config(text="Please select a future date.", fg="red")
        else:
            class_datetime = datetime.datetime.combine(selected_date,
                                                       datetime.datetime.strptime(selected_time, "%H:%M").time())
            if class_datetime < current_datetime:
                lbl_rslt.config(text="Please select a future time.", fg="red")
            else:
                entry_class_datetime.delete(0, END)
                entry_class_datetime.insert(END, class_datetime.strftime("%Y-%m-%d %H:%M"))

    def save_class():
        instructor_name = instructor_var.get()
        class_datetime = entry_class_datetime.get().strip()

        if class_datetime == "":
            lbl_rslt.config(text="Please choose a class date and time.", fg="red")
        else:
            selected_datetime = datetime.datetime.strptime(class_datetime, "%Y-%m-%d %H:%M")
            current_datetime = datetime.datetime.now()
            if selected_datetime < current_datetime:
                lbl_rslt.config(text="Please choose a future date and time.", fg="red")
            else:
                try:
                    cursor.execute(
                        "SELECT mem_id FROM `user` WHERE `role` = 'Instructor' AND `firstname` || ' ' || `lastname` = ?",
                        (instructor_name,))
                    instructor_id = cursor.fetchone()[0]

                    cursor.execute(
                        "SELECT * FROM `class_plan` WHERE instructor_id = ? AND class_datetime = ?",
                        (instructor_id, class_datetime)
                    )
                    existing_class = cursor.fetchone()

                    if existing_class:
                        lbl_rslt.config(text="Selected instructor is busy this term.", fg="red")
                    else:
                        cursor.execute(
                            "INSERT INTO `class_plan` (student_id, instructor_id, instructor_name, class_datetime, status, displayed) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, instructor_id, instructor_name, class_datetime, 'Proposed', 0)
                        )

                        conn.commit()

                        lbl_rslt.config(text="Class proposed successfully!", fg="green")

                except Exception as e:
                    lbl_rslt.config(text="Error saving class: " + str(e), fg="red")

        class_plan_window.after(3000, lambda: lbl_rslt.config(text=""))

    btn_select_date_time = Button(class_plan_window, text="Select Date and Time", command=on_date_time_selected)
    btn_select_date_time.pack()

    btn_save_class = Button(class_plan_window, text="Save Class", command=save_class)
    btn_save_class.pack()

    lbl_rslt = Label(class_plan_window, text="", fg="red")
    lbl_rslt.pack()


def manage_classes():
    manage_classes_window = Toplevel(root)
    manage_classes_window.title("Manage Classes")

    lbl_proposed_classes = Label(manage_classes_window, text="Proposed Classes:")
    lbl_proposed_classes.pack()

    cursor.execute("SELECT mem_id FROM `user` WHERE `username` = ?", (USERNAME.get(),))
    instructor_id = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM `class_plan` WHERE `status` = 'Proposed' AND `instructor_id` = ?", (instructor_id,))
    proposed_classes = cursor.fetchall()

    for class_plan in proposed_classes:
        class_id = class_plan[0]
        student_id = class_plan[1]
        class_datetime = class_plan[4]

        cursor.execute("SELECT firstname, lastname FROM `user` WHERE `mem_id` = ?", (student_id,))
        student_name = cursor.fetchone()
        student_first_name, student_last_name = student_name

        class_info = f"Student Name: {student_first_name} {student_last_name}\nClass Date and Time: {class_datetime}\n"

        class_label = Label(manage_classes_window, text=class_info)
        class_label.pack()

        accept_button = Button(manage_classes_window, text="Accept")
        reject_button = Button(manage_classes_window, text="Reject")

        accept_button.config(
            command=lambda clss_id=class_id, clss_label=class_label, accept_btn=accept_button, reject_btn=reject_button:
            accept_class(clss_id, clss_label, accept_btn, reject_btn))
        accept_button.pack()

        reject_button.config(
            command=lambda clss_id=class_id, clss_label=class_label, accept_btn=accept_button, reject_btn=reject_button:
            reject_class(clss_id, clss_label, accept_btn, reject_btn))
        reject_button.pack()

    def accept_class(clss_id, clss_label, accept_btn, reject_btn):
        try:
            cursor.execute("UPDATE `class_plan` SET `status` = 'Scheduled' WHERE `class_id` = ?", (clss_id,))
            conn.commit()
            lbl_res.config(text="Class accepted successfully!", fg="green")
            clss_label.destroy()
            accept_btn.destroy()
            reject_btn.destroy()
        except Exception as e:
            lbl_res.config(text="Error accepting class: " + str(e), fg="red")

    def reject_class(clss_id, clss_label, accept_btn, reject_btn):
        try:
            cursor.execute("UPDATE `class_plan` SET `status` = 'Rejected' WHERE `class_id` = ?", (clss_id,))
            conn.commit()
            lbl_res.config(text="Class rejected successfully!", fg="green")
            clss_label.destroy()
            accept_btn.destroy()
            reject_btn.destroy()
        except Exception as e:
            lbl_res.config(text="Error rejecting class: " + str(e), fg="red")

    lbl_res = Label(manage_classes_window, text="", fg="red")
    lbl_res.pack()

    manage_classes_window.after(3000, lambda: lbl_res.config(text=""))


def view_classes():
    global role, idd
    view_classes_window = Toplevel(root)
    view_classes_window.title("View Classes")

    cursor.execute("SELECT mem_id, role FROM `user` WHERE `username` = ?", (USERNAME.get(),))
    row = cursor.fetchone()
    if row is not None:
        role = row[1]
        idd = row[0]

    if role == "Student":
        cursor.execute(
            "SELECT class_id, instructor_id, instructor_name, class_datetime, status FROM `class_plan` WHERE `student_id` = ? AND status = 'Scheduled' AND class_datetime > datetime('now')",
            (idd,))
    elif role == "Instructor":
        cursor.execute(
            "SELECT class_id, student_id, class_datetime, status FROM `class_plan` WHERE `instructor_id` = ? AND status = 'Scheduled' AND class_datetime > datetime('now')",
            (idd,))
    else:
        cursor.execute(
            "SELECT class_id, student_id, instructor_id, class_datetime, status FROM `class_plan` WHERE status = 'Scheduled'")

    classes = cursor.fetchall()

    if not classes:
        lbl_no_classes = Label(view_classes_window, text="No classes found.", font=('arial', 12))
        lbl_no_classes.pack(pady=10)
    else:
        lbl_class_info = Label(view_classes_window, text="Class Information", font=('arial', 12, 'bold'))
        lbl_class_info.pack(pady=10)

        if role == "Student":
            tree = ttk.Treeview(view_classes_window,
                                columns=("class_id", "instructor_id", "instructor_name", "class_datetime"),
                                show="headings")
            tree.heading("class_id", text="Class ID")
            tree.heading("instructor_id", text="Instructor ID")
            tree.heading("instructor_name", text="Instructor Name")
            tree.heading("class_datetime", text="Date and Time")

            for class_info in classes:
                tree.insert("", "end", values=class_info)

            tree.pack(pady=10)
        elif role == "Instructor":
            tree = ttk.Treeview(view_classes_window,
                                columns=("class_id", "student_id", "class_datetime"),
                                show="headings")
            tree.heading("class_id", text="Class ID")
            tree.heading("student_id", text="Student ID")
            tree.heading("class_datetime", text="Date and Time")

            for class_info in classes:
                tree.insert("", "end", values=class_info)

            tree.pack(pady=10)
        else:
            tree = ttk.Treeview(view_classes_window,
                                columns=("class_id", "student_id", "instructor_id", "class_datetime"),
                                show="headings")
            tree.heading("class_id", text="Class ID")
            tree.heading("student_id", text="Student ID")
            tree.heading("instructor_id", text="Instructor ID")
            tree.heading("class_datetime", text="Date and Time")

            for class_info in classes:
                tree.insert("", "end", values=class_info)

            tree.pack(pady=10)


def rate():
    rate_window = Toplevel(root)
    rate_window.title("Rate")

    cursor.execute("SELECT mem_id FROM `user` WHERE `username` = ?", (USERNAME.get(),))
    user_id = cursor.fetchone()[0]

    entry_student_id = Entry(rate_window, state="readonly")
    entry_student_id.insert(END, user_id)

    lbl_instructor_name = Label(rate_window, text="Instructor Name:")
    lbl_instructor_name.pack()

    instructor_list = []
    cursor.execute("SELECT * FROM `user` WHERE `role` = 'Instructor'")
    instructors = cursor.fetchall()
    for instructor in instructors:
        instructor_list.append(instructor[3] + " " + instructor[4])

    instructor_var = StringVar(rate_window)
    instructor_var.set(instructor_list[0])

    instructor_dropdown = OptionMenu(rate_window, instructor_var, *instructor_list)
    instructor_dropdown.pack()

    rating_frame = Frame(rate_window)
    rating_frame.pack()

    rating_value = IntVar()

    for i in range(1, 6):
        rating_button = Radiobutton(rating_frame, text=str(i), variable=rating_value, value=i)
        rating_button.grid(row=0, column=i - 1)

    lbl_feedback = Label(rate_window, text="Feedback:")
    lbl_feedback.pack()
    entry_feedback = Entry(rate_window, textvariable=FEEDBACK)
    entry_feedback.pack()

    lbl_res = Label(rate_window, text="", fg="red")
    lbl_res.pack()

    def submit_rating():
        if rating_value.get() == 0:
            lbl_res.config(text="Please select a rating.", fg="red")
        elif instructor_var.get() == "" or rating_value.get() == "":
            lbl_res.config(text="Please enter both Instructor Name and Rating.", fg="red")
        else:
            instructor_fullname = instructor_var.get().split(" ")
            instructor_first_name = instructor_fullname[0]
            instructor_last_name = instructor_fullname[1]

            cursor.execute(
                "INSERT INTO `rating` (rating, feedback, instructor_first_name, instructor_last_name) VALUES (?, ?, ?, ?)",
                (str(rating_value.get()), str(entry_feedback.get()), instructor_first_name, instructor_last_name)
            )
            conn.commit()
            lbl_res.config(text="Rating submitted successfully!", fg="green")
            rating_value.set(0)
            entry_feedback.delete(0, END)

    btn_submit_rating = Button(rate_window, text="Submit Rating", command=submit_rating)
    btn_submit_rating.pack()


def report_analyze_progress():
    report_analyze_window = Toplevel(root)
    report_analyze_window.title("Analyze/Report")

    lbl_back = Label(report_analyze_window, text="Back", fg="Blue", font=('arial', 12))
    lbl_back.grid(row=0, column=0, sticky=W)
    lbl_back.bind('<Button-1>', lambda event: MainForm())

    lbl_report = Label(report_analyze_window, text="Report", font=('arial', 18), bd=18)
    lbl_report.grid(row=1, column=0)
    lbl_analysis = Label(report_analyze_window, text="Analysis", font=('arial', 18), bd=18)
    lbl_analysis.grid(row=1, column=1)

    btn_report_options = Button(report_analyze_window, text="Select Report Options", font=('arial', 14), width=20,
                                command=show_report_options)
    btn_report_options.grid(row=2, column=0, pady=10)
    btn_analysis_options = Button(report_analyze_window, text="Select Analysis Options", font=('arial', 14), width=20,
                                  command=show_analysis_options)
    btn_analysis_options.grid(row=2, column=1, pady=10)


def show_report_options():
    clear_output(root)
    report_options_window = Toplevel(root)
    report_options_window.title("Select Report Options")

    lbl_from_date = Label(report_options_window, text="From Date (YYYY-MM-DD):", font=('arial', 14))
    lbl_from_date.grid(row=0, column=0, sticky=W)
    entry_from_date = Entry(report_options_window, font=('arial', 14))
    entry_from_date.grid(row=0, column=1)

    lbl_to_date = Label(report_options_window, text="To Date (YYYY-MM-DD):", font=('arial', 14))
    lbl_to_date.grid(row=1, column=0, sticky=W)
    entry_to_date = Entry(report_options_window, font=('arial', 14))
    entry_to_date.grid(row=1, column=1)

    recipient_choice = StringVar(report_options_window)
    recipient_choice.set("All Students")
    lbl_recipient_choice = Label(report_options_window, text="Recipient:", font=('arial', 14))
    lbl_recipient_choice.grid(row=2, column=0, sticky=W)
    rb_all_students = Radiobutton(report_options_window, text="All Students", font=('arial', 14),
                                  variable=recipient_choice, value="All Students")
    rb_all_students.grid(row=2, column=1, sticky=W)
    rb_one_student = Radiobutton(report_options_window, text="One Student", font=('arial', 14),
                                 variable=recipient_choice, value="One Student",
                                 command=lambda: toggle_choose_user(report_options_window, recipient_choice.get()))
    rb_one_student.grid(row=3, column=1, sticky=W)

    btn_generate_report = Button(report_options_window, text="Generate Report", font=('arial', 14),
                                 command=lambda: generate_report(report_options_window, recipient_choice.get(),
                                                                 entry_from_date.get(), entry_to_date.get()))
    btn_generate_report.grid(row=4, column=0, pady=10)


def show_analysis_options():
    clear_output(root)
    analysis_options_window = Toplevel(root)
    analysis_options_window.title("Select Analysis Options")

    lbl_from_date = Label(analysis_options_window, text="From Date (YYYY-MM-DD):", font=('arial', 14))
    lbl_from_date.grid(row=0, column=0, sticky=W)
    entry_from_date = Entry(analysis_options_window, font=('arial', 14))
    entry_from_date.grid(row=0, column=1)

    lbl_to_date = Label(analysis_options_window, text="To Date (YYYY-MM-DD):", font=('arial', 14))
    lbl_to_date.grid(row=1, column=0, sticky=W)
    entry_to_date = Entry(analysis_options_window, font=('arial', 14))
    entry_to_date.grid(row=1, column=1)

    recipient_choice = StringVar(analysis_options_window)
    recipient_choice.set("All Students")
    lbl_recipient_choice = Label(analysis_options_window, text="Recipient:", font=('arial', 14))
    lbl_recipient_choice.grid(row=2, column=0, sticky=W)
    rb_all_students = Radiobutton(analysis_options_window, text="All Students", font=('arial', 14),
                                  variable=recipient_choice, value="All Students")
    rb_all_students.grid(row=2, column=1, sticky=W)
    rb_one_student = Radiobutton(analysis_options_window, text="One Student", font=('arial', 14),
                                 variable=recipient_choice, value="One Student",
                                 command=lambda: toggle_choose_user(analysis_options_window, recipient_choice.get()))
    rb_one_student.grid(row=3, column=1, sticky=W)

    btn_perform_analysis = Button(analysis_options_window, text="Perform Analysis", font=('arial', 14),
                                  command=lambda: perform_analysis(analysis_options_window, recipient_choice.get(),
                                                                   entry_from_date.get(), entry_to_date.get()))
    btn_perform_analysis.grid(row=4, column=0, pady=10)


def toggle_choose_user(window, choice):
    if hasattr(window, 'lbl_choose_user'):
        window.lbl_choose_user.grid_remove()

    if hasattr(window, 'user_option_menu'):
        window.user_option_menu.grid_remove()

    if choice == "One Student":
        window.lbl_choose_user = Label(window, text="Choose User:", font=('arial', 14))
        window.lbl_choose_user.grid(row=5, column=0, sticky=W)

        users_list = []
        cursor.execute("SELECT * FROM `user` WHERE `role` = 'Student'")
        users = cursor.fetchall()
        for user in users:
            users_list.append(user[3] + " " + user[4])

        user_var = StringVar(window)
        user_var.set(users_list[0])

        window.user_option_menu = OptionMenu(window, user_var, *users_list)
        window.user_option_menu.grid(row=5, column=1, sticky=W)
        window.user_var = user_var
    else:
        pass


def get_selected_student_id(user_var):
    selected_user = user_var.get()
    first_name, last_name = selected_user.split(" ")

    cursor.execute("SELECT mem_id FROM user WHERE role = 'Student' AND firstname = ? AND lastname = ?",
                   (first_name, last_name))
    result = cursor.fetchone()
    if result:
        selected_student_id = result[0]
        return selected_student_id
    return None


def generate_report(window, recipient_choice, from_date, to_date):
    clear_output(window)
    if not validate_date(from_date) or not validate_date(to_date):
        error_label = Label(window, text="Invalid date format. Please use YYYY-MM-DD.", font=('arial', 14), fg="red")
        error_label.grid(row=5, column=0, columnspan=2)
        return
    if recipient_choice == "All Students":
        recipient = "All Students"
        cursor.execute(
            "SELECT payment_id, student_id, what_for, amount, payment_date FROM payment WHERE payment_date >= ? AND payment_date <= ?",
            (from_date, to_date))
    else:
        selected_student_id = get_selected_student_id(window.user_var)
        if selected_student_id:
            cursor.execute(
                "SELECT payment_id, student_id, what_for, amount, payment_date FROM payment WHERE student_id = ? AND payment_date >= ? AND payment_date <= ?",
                (selected_student_id, from_date, to_date))
            recipient = f"Student ID: {selected_student_id}"
        else:
            recipient = "No student selected"

    payments = cursor.fetchall()

    columns = ["payment_id", "student_id", "what_for", "amount", "payment_date"]
    df = pd.DataFrame(payments, columns=columns)

    report_label = Label(window, text="Generated Report", font=('arial', 18), bd=18)
    report_label.grid(row=6, column=0, columnspan=2)

    report_info_label = Label(window, text=f"Recipient: {recipient}", font=('arial', 14), bd=10)
    report_info_label.grid(row=7, column=0, columnspan=2)

    data_label = Label(window, text=df.to_string())
    data_label.grid(row=8, column=0, columnspan=2)


def perform_analysis(window, recipient_choice, from_date, to_date):
    clear_output(window)
    if not validate_date(from_date) or not validate_date(to_date):
        error_label = Label(window, text="Invalid date format. Please use YYYY-MM-DD.", font=('arial', 14), fg="red")
        error_label.grid(row=5, column=0, columnspan=2)
        return
    if recipient_choice == "All Students":
        recipient = "All Students"
        cursor.execute(
            "SELECT student_id, SUM(amount) FROM payment WHERE payment_date >= ? AND payment_date <= ? GROUP BY student_id",
            (from_date, to_date))
    else:
        selected_student_id = get_selected_student_id(window.user_var)
        if selected_student_id:
            cursor.execute(
                "SELECT student_id, SUM(amount) FROM payment WHERE student_id = ? AND payment_date >= ? AND payment_date <= ? GROUP BY student_id",
                (selected_student_id, from_date, to_date))
            recipient = f"Student ID: {selected_student_id}"
        else:
            recipient = "No student selected"

    analysis = cursor.fetchall()

    columns = ["student_id", "total_amount"]
    df = pd.DataFrame(analysis, columns=columns)

    analysis_label = Label(window, text="Analysis Result", font=('arial', 18), bd=18)
    analysis_label.grid(row=6, column=0, columnspan=2)

    analysis_info_label = Label(window, text=f"Recipient: {recipient}", font=('arial', 14), bd=10)
    analysis_info_label.grid(row=7, column=0, columnspan=2)

    data_label = Label(window, text=df.to_string())
    data_label.grid(row=8, column=0, columnspan=2)


def validate_date(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def clear_output(window):
    for widget in window.winfo_children():
        if isinstance(widget, Label) and widget.cget("text") != "From Date (YYYY-MM-DD):" and widget.cget("text") != "To Date (YYYY-MM-DD):" and widget.cget("text") != "Recipient:" and widget.cget("text") != "Choose User:":
            widget.grid_remove()


# ========================================MENUBAR WIDGETS==================================
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=Exit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

LoginForm()
root.mainloop()

# ========================================INITIALIZATION===================================
if __name__ == '__main__':
    root.mainloop()
