from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import pymysql
from tkinter.ttk import Treeview
from tkinter.filedialog import askopenfilename


def insert_stu():
    def add_stu():
        try:
            cur.execute("CALL AddStudent('%s', '%s', '%s', %s, %s, '%s', '%s', '%s')" %
                        (entry_id.get(), entry_name.get(), entry_gender.get(), entry_age.get(),
                         entry_class_id.get(), entry_birth_date.get(), entry_contact_info.get(), entry_photo.get()))
            db.commit()
            messagebox.showinfo("提示", "学生信息添加成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def select_photo():
        filepath = askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            entry_photo.delete(0, END)
            entry_photo.insert(0, filepath)

    root_insert = Toplevel()
    root_insert.title("添加学生信息")
    root_insert.geometry("400x350")

    labels = ["学号：", "姓名：", "性别：", "年龄：", "班级ID：", "出生日期：", "联系方式：", "照片："]
    entries = []

    for i, label_text in enumerate(labels):
        label = Label(root_insert, text=label_text)
        label.grid(row=i, column=0, padx=10, pady=5, sticky=E)
        entry = Entry(root_insert)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    entry_id, entry_name, entry_gender, entry_age, entry_class_id, entry_birth_date, entry_contact_info, entry_photo = entries

    Button(root_insert, text="选择照片", command=select_photo).grid(row=7, column=2, padx=10, pady=5)
    Button(root_insert, text="提交", command=add_stu).grid(row=8, column=0, padx=10, pady=10)
    Button(root_insert, text="退出", command=root_insert.destroy).grid(row=8, column=1, padx=10, pady=10)


def delete_stu():
    def del_stu():
        try:
            cur.execute("CALL DeleteStudent(%s)", (entry_id.get(),))
            db.commit()
            messagebox.showinfo("提示", "学生信息删除成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_delete = Toplevel()
    root_delete.title("删除学生信息")
    root_delete.geometry("300x100")

    Label(root_delete, text="学号：").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    entry_id = Entry(root_delete)
    entry_id.grid(row=0, column=1, padx=10, pady=5)

    Button(root_delete, text="提交", command=del_stu).grid(row=1, column=0, padx=10, pady=10)
    Button(root_delete, text="退出", command=root_delete.destroy).grid(row=1, column=1, padx=10, pady=10)


def change_stu():
    def update_stu():
        cur.execute("SELECT * FROM Student WHERE StudentID = '%s'" % entry_id.get())
        result = cur.fetchone()
        name = entry_name.get() if entry_name.get() else result['Name']
        age = entry_age.get() if entry_age.get() else result['Age']
        class_id = entry_class_id.get() if entry_class_id.get() else result['ClassID']
        contact_info = entry_contact_info.get() if entry_contact_info.get() else result['ContactInfo']
        photo = entry_photo.get() if entry_photo.get() else result['Photo']
        try:
            cur.execute("CALL UpdateStudent('%s', '%s', %s, %s, '%s', '%s')" %
                        (entry_id.get(), name, age, class_id, contact_info, photo))
            db.commit()
            messagebox.showinfo("提示", "学生信息更新成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def select_photo():
        filepath = askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            entry_photo.delete(0, END)
            entry_photo.insert(0, filepath)

    root_change = Toplevel()
    root_change.title("修改学生信息")
    root_change.geometry("400x300")

    labels = ["*需要修改的学生学号：", "修改后姓名：", "修改后年龄：", "修改后班级ID：", "修改后联系方式：", "修改后照片："]
    entries = []

    for i, label_text in enumerate(labels):
        label = Label(root_change, text=label_text)
        label.grid(row=i, column=0, padx=10, pady=5, sticky=E)
        entry = Entry(root_change)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    entry_id, entry_name, entry_age, entry_class_id, entry_contact_info, entry_photo = entries

    Button(root_change, text="选择照片", command=select_photo).grid(row=5, column=2, padx=10, pady=5)
    Button(root_change, text="提交", command=update_stu).grid(row=6, column=0, padx=10, pady=10)
    Button(root_change, text="退出", command=root_change.destroy).grid(row=6, column=1, padx=10, pady=10)


def sel_stu():
    def search_stu():
        try:
            for widget in frame_result.winfo_children():
                widget.destroy()

            cur.execute("CALL SearchStudent('%s')" % entry_id.get())
            result = cur.fetchone()
            if result:
                labels = [
                    ("姓名", result['Name']),
                    ("性别", result["Gender"]),
                    ("年龄", result["Age"]),
                    ("出生日期", result["BirthDate"]),
                    ("联系方式", result["ContactInfo"]),
                    ("班级ID", result["clsID"]),
                    ("专业", result["Major"]),
                    ("班主任", result["Teacher"])
                ]
                for i, (label_text, value) in enumerate(labels):
                    Label(frame_result, text=f"{label_text}: {value}").grid(row=i+2, column=0, columnspan=2, padx=10, pady=5)

                if result['Photo']:
                    img = Image.open(result['Photo'])
                    img = img.resize((250, 250), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    Label(frame_result, image=photo).grid(row=2, column=2, rowspan=8, padx=10, pady=5)
                    frame_result.photo = photo

            else:
                messagebox.showinfo("提示", "未找到相关记录")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_sel_stu = Toplevel()
    root_sel_stu.title("查询学生信息")
    root_sel_stu.geometry("600x400")

    Label(root_sel_stu, text="学号：").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    entry_id = Entry(root_sel_stu)
    entry_id.grid(row=0, column=1, padx=10, pady=5)

    Button(root_sel_stu, text="查询", command=search_stu).grid(row=1, column=0, padx=10, pady=10)
    Button(root_sel_stu, text="退出", command=root_sel_stu.destroy).grid(row=1, column=1, padx=10, pady=10)

    frame_result = Frame(root_sel_stu)
    frame_result.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

# 创建学生信息管理分窗口
def create_stu():
    root1 = Tk()
    root1.title("学生信息管理")
    root1.config(width=600)
    root1.config(height=600)

    button_insert_stu = Button(root1, text="添加学生信息", command=insert_stu)
    button_insert_stu.place(x=200, y=50, height=40, width=200)

    button_delete_stu = Button(root1, text="删除学生信息", command=delete_stu)
    button_delete_stu.place(x=200, y=150, height=40, width=200)

    button_change_stu = Button(root1, text="修改学生信息", command=change_stu)
    button_change_stu.place(x=200, y=250, height=40, width=200)

    button_sel_stu = Button(root1, text="查询学生信息", command=sel_stu)
    button_sel_stu.place(x=200, y=350, height=40, width=200)

    button_del = Button(root1, text="退出", command=root1.destroy)
    button_del.place(x=200, y=450, height=40, width=200)

    root1.mainloop()


def insert_score():
    def add_score():
        try:
            cur.execute("CALL AddCourseGrade('%s', %s)" % (entry_student_id.get(), entry_course_id.get()))
            db.commit()
            messagebox.showinfo("提示", "选课信息录入成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_insert_score = Toplevel()
    root_insert_score.title("录入选课信息")
    root_insert_score.geometry("300x150")

    Label(root_insert_score, text="学生学号：").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    entry_student_id = Entry(root_insert_score)
    entry_student_id.grid(row=0, column=1, padx=10, pady=5)

    Label(root_insert_score, text="课程ID：").grid(row=1, column=0, padx=10, pady=5, sticky=E)
    entry_course_id = Entry(root_insert_score)
    entry_course_id.grid(row=1, column=1, padx=10, pady=5)

    Button(root_insert_score, text="提交", command=add_score).grid(row=2, column=0, padx=10, pady=10)
    Button(root_insert_score, text="退出", command=root_insert_score.destroy).grid(row=2, column=1, padx=10, pady=10)


def change_score():
    def update_score():
        try:
            cur.execute("CALL UpdateGrade('%s', %s, %s)" %
                        (entry_student_id.get(), entry_course_id.get(), entry_score.get()))
            db.commit()
            messagebox.showinfo("提示", "成绩更新成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_change_score = Toplevel()
    root_change_score.title("修改课程成绩")
    root_change_score.geometry("300x200")

    Label(root_change_score, text="学生学号：").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    entry_student_id = Entry(root_change_score)
    entry_student_id.grid(row=0, column=1, padx=10, pady=5)

    Label(root_change_score, text="课程ID：").grid(row=1, column=0, padx=10, pady=5, sticky=E)
    entry_course_id = Entry(root_change_score)
    entry_course_id.grid(row=1, column=1, padx=10, pady=5)

    Label(root_change_score, text="成绩：").grid(row=2, column=0, padx=10, pady=5, sticky=E)
    entry_score = Entry(root_change_score)
    entry_score.grid(row=2, column=1, padx=10, pady=5)

    Button(root_change_score, text="提交", command=update_score).grid(row=3, column=0, padx=10, pady=10)
    Button(root_change_score, text="退出", command=root_change_score.destroy).grid(row=3, column=1, padx=10, pady=10)


def sel_score():
    def search_score():
        for item in tree.get_children():
            tree.delete(item)
        try:
            if entry_course_id.get() == "":
                cur.execute("CALL SearchCourse('%s')" % entry_student_id.get())
                result = cur.fetchall()
                if not result:
                    messagebox.showinfo("提示", "未找到相关记录")
                for item in result:
                    tree.insert("", "end", values=(
                        item["cs_id"], item["CourseName"], item["Teacher"], item["Classroom"], item["Score"]))
            else:
                cur.execute("SELECT GetGrade('%s', %s) AS Score" % (entry_student_id.get(), entry_course_id.get()))
                result = cur.fetchone()
                if not result:
                    messagebox.showinfo("提示", "未找到相关记录")
                else:
                    Label(root_search_score, text="成绩: " + str(result['Score'])).grid(row=2, column=0)

        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_search_score = Toplevel()
    root_search_score.title("查询选课及成绩信息")
    root_search_score.geometry("600x400")

    Label(root_search_score, text="*学生学号：").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    entry_student_id = Entry(root_search_score)
    entry_student_id.grid(row=0, column=1, padx=10, pady=5)

    Label(root_search_score, text="课程ID：").grid(row=1, column=0, padx=10, pady=5, sticky=E)
    entry_course_id = Entry(root_search_score)
    entry_course_id.grid(row=1, column=1, padx=10, pady=5)

    Button(root_search_score, text="查询", command=search_score).grid(row=3, column=0, padx=10, pady=10)
    Button(root_search_score, text="退出", command=root_search_score.destroy).grid(row=3, column=1, padx=10, pady=10)

    tree = Treeview(root_search_score, columns=("课程ID", "课程名称", "教师", "教室", "成绩"), show="headings")
    tree.heading("课程ID", text="课程ID")
    tree.heading("课程名称", text="课程名称")
    tree.heading("教师", text="教师")
    tree.heading("教室", text="教室")
    tree.heading("成绩", text="成绩")
    tree.column("课程ID", width=100, anchor="center")
    tree.column("课程名称", width=100, anchor="center")
    tree.column("教师", width=100, anchor="center")
    tree.column("教室", width=100, anchor="center")
    tree.column("成绩", width=100, anchor="center")
    tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)


# 创建选课及课程成绩管理分窗口
def create_score():
    root2 = Tk()
    root2.title("选课及课程成绩管理")
    root2.config(width=600)
    root2.config(height=600)

    # 创建按钮
    button_insert_score = Button(root2, text="录入选课", command=insert_score)
    button_insert_score.place(x=200, y=100, height=40, width=200)

    button_change_score = Button(root2, text="修改课程成绩", command=change_score)
    button_change_score.place(x=200, y=200, height=40, width=200)

    button_sel_score = Button(root2, text="查询选课及成绩", command=sel_score)
    button_sel_score.place(x=200, y=300, height=40, width=200)

    # 退出键
    button_del = Button(root2, text="退出", command=root2.destroy)
    button_del.place(x=200, y=400, height=40, width=200)

    root2.mainloop()


def insert_course():
    def add_course():
        try:
            cur.execute("INSERT INTO Course(CourseID, CourseName, Teacher, Classroom) VALUES (%s, '%s', '%s', '%s')" %
                        (entry_course_id.get(), entry_course_name.get(), entry_teacher.get(), entry_classroom.get()))
            db.commit()
            messagebox.showinfo("提示", "课程信息添加成功")
            entry_course_id.delete(0, END)
            entry_course_name.delete(0, END)
            entry_teacher.delete(0, END)
            entry_classroom.delete(0, END)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_insert_course = Toplevel()
    root_insert_course.title("添加课程信息")
    root_insert_course.geometry("400x250")

    labels = ["课程ID：", "课程名称：", "教师：", "教室："]
    entries = []

    for i, label_text in enumerate(labels):
        label = Label(root_insert_course, text=label_text)
        label.grid(row=i, column=0, padx=10, pady=5, sticky=E)
        entry = Entry(root_insert_course)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    entry_course_id, entry_course_name, entry_teacher, entry_classroom = entries

    Button(root_insert_course, text="提交", command=add_course).grid(row=5, column=0, padx=10, pady=10)
    Button(root_insert_course, text="退出", command=root_insert_course.destroy).grid(row=5, column=1, padx=10, pady=10)


def delete_course():
    def del_course():
        try:
            cur.execute("DELETE FROM Course WHERE CourseID = %s" % entry_course_id.get())
            db.commit()
            messagebox.showinfo("提示", "课程信息删除成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_delete_course = Toplevel()
    root_delete_course.title("删除课程信息")
    root_delete_course.geometry("300x100")

    Label(root_delete_course, text="课程ID：").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    entry_course_id = Entry(root_delete_course)
    entry_course_id.grid(row=0, column=1, padx=10, pady=5)

    Button(root_delete_course, text="提交", command=del_course).grid(row=1, column=0, padx=10, pady=10)
    Button(root_delete_course, text="退出", command=root_delete_course.destroy).grid(row=1, column=1, padx=10, pady=10)


def change_course():
    def update_course():
        cur.execute("SELECT * FROM Course WHERE CourseID = %s" % entry_course_id.get())
        result = cur.fetchone()
        course = entry_course_name.get() if entry_course_name.get() else result['CourseName']
        teacher = entry_teacher.get() if entry_teacher.get() else result['Teacher']
        classroom = entry_classroom.get() if entry_classroom.get() else result['Classroom']
        try:
            cur.execute("UPDATE Course SET CourseName = '%s', Teacher = '%s', Classroom = '%s' WHERE CourseID = %s" %
                        (course, teacher, classroom,
                         eval(entry_course_id.get())))
            db.commit()
            messagebox.showinfo("提示", "课程信息更新成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    root_change_course = Toplevel()
    root_change_course.title("修改课程信息")
    root_change_course.geometry("400x250")

    labels = ["*需要修改的课程ID：", "修改后课程名称：", "修改后教师：", "修改后教室："]
    entries = []

    for i, label_text in enumerate(labels):
        label = Label(root_change_course, text=label_text)
        label.grid(row=i, column=0, padx=10, pady=5, sticky=E)
        entry = Entry(root_change_course)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    entry_course_id, entry_course_name, entry_teacher, entry_classroom = entries

    Button(root_change_course, text="提交", command=update_course).grid(row=5, column=0, padx=10, pady=10)
    Button(root_change_course, text="退出", command=root_change_course.destroy).grid(row=5, column=1, padx=10, pady=10)


# 可以根据课程ID，课程名，教师，教室四个条件中任意选择容易几个条件来查询
def sel_course():
    def search_course():
        for item in Tree.get_children():
            Tree.delete(item)

        try:
            query = "SELECT * FROM Course WHERE 1=1"
            params = []

            if entry_course_id.get():
                query += " AND CourseID = %s"
                params.append((entry_course_id.get()))
            if entry_course_name.get():
                query += " AND CourseName = '%s'"
                params.append(entry_course_name.get())
            if entry_teacher.get():
                query += " AND Teacher = '%s'"
                params.append(entry_teacher.get())
            if entry_classroom.get():
                query += " AND Classroom = '%s'"
                params.append(entry_classroom.get())

            cur.execute(query % tuple(params))
            results = cur.fetchall()
            if results:
                for result in results:
                    Tree.insert("", "end", values=(
                        result["CourseID"], result["CourseName"], result["Teacher"], result["Classroom"]))
            else:
                messagebox.showinfo("提示", "未找到相关记录")
        except Exception as e:
            messagebox.showerror("错误", str(e))
        entry_course_id.delete(0, END)
        entry_course_name.delete(0, END)
        entry_teacher.delete(0, END)
        entry_classroom.delete(0, END)

    root_search_course = Tk()
    root_search_course.title("查询课程信息")

    Label(root_search_course, text="课程ID：").grid(row=0, column=0)
    entry_course_id = Entry(root_search_course)
    entry_course_id.grid(row=0, column=1)

    Label(root_search_course, text="课程名称：").grid(row=1, column=0)
    entry_course_name = Entry(root_search_course)
    entry_course_name.grid(row=1, column=1)

    Label(root_search_course, text="教师：").grid(row=2, column=0)
    entry_teacher = Entry(root_search_course)
    entry_teacher.grid(row=2, column=1)

    Label(root_search_course, text="教室：").grid(row=3, column=0)
    entry_classroom = Entry(root_search_course)
    entry_classroom.grid(row=3, column=1)

    Button(root_search_course, text="查询", command=search_course).grid(row=5, column=0)
    Button(root_search_course, text="退出", command=root_search_course.destroy).grid(row=5, column=1)

    Tree = Treeview(root_search_course, columns=("课程ID", "课程名称", "教师", "教室"), show="headings")
    Tree.heading("课程ID", text="课程ID", anchor="center")
    Tree.heading("课程名称", text="课程名称", anchor="center")
    Tree.heading("教师", text="教师", anchor="center")
    Tree.heading("教室", text="教室", anchor="center")
    Tree.column("课程ID", width=100)
    Tree.column("课程名称", width=100)
    Tree.column("教师", width=100)
    Tree.column("教室", width=100)
    Tree.grid(row=7, columnspan=2)

    root_search_course.mainloop()


# 创建课程管理分窗口
def create_course():
    root3 = Tk()
    root3.title("课程管理")
    root3.config(width=600)
    root3.config(height=600)

    button_insert_course = Button(root3, text="添加课程", command=insert_course)
    button_insert_course.place(x=200, y=100, height=40, width=200)

    button_delete_course = Button(root3, text="删除课程", command=delete_course)
    button_delete_course.place(x=200, y=200, height=40, width=200)

    button_change_course = Button(root3, text="修改课程", command=change_course)
    button_change_course.place(x=200, y=300, height=40, width=200)

    button_sel_course = Button(root3, text="查询课程", command=sel_course)
    button_sel_course.place(x=200, y=400, height=40, width=200)

    button_del = Button(root3, text="退出", command=root3.destroy)
    button_del.place(x=200, y=500, height=40, width=200)

    root3.mainloop()


# 分别录入奖励和惩罚信息
def insert_rp():
    def insert_reward():
        sql = "insert into Reward(StudentID, Detail) values('%s', '%s');"
        cur.execute(sql % (entryId.get(), entryDetail.get()))
        db.commit()
        messagebox.showinfo("提示", "录入成功")

    def insert_punish():
        sql = "insert into Punish(StudentID, Detail) values('%s', '%s');"
        cur.execute(sql % (entryId.get(), entryDetail.get()))
        db.commit()
        messagebox.showinfo("提示", "录入成功")

    root4 = Tk()
    root4.title("录入奖惩信息")
    root4.config(width=600)
    root4.config(height=600)

    # 选择类型，奖励或惩罚

    label = Label(root4, text="学号：")
    entryId = Entry(root4)
    entryId.place(x=110, y=20, height=40, width=200)
    label.place(x=30, y=20, height=40, width=80)
    labelDetail = Label(root4, text="内容：")
    entryDetail = Entry(root4)
    entryDetail.place(x=110, y=100, height=40, width=200)
    labelDetail.place(x=30, y=100, height=40, width=80)
    button_reward = Button(root4, text="录入奖励", command=insert_reward)
    button_reward.place(x=100, y=200, height=40, width=100)
    button_punish = Button(root4, text="录入惩罚", command=insert_punish)
    button_punish.place(x=250, y=200, height=40, width=100)


# 创建奖惩管理分窗口
def create_reward_punish():
    # 根据学号查询奖惩信息，分别展示奖励和惩罚列表
    def sel_rp():
        sql1 = "select * from Reward where StudentID = '%s'"
        sql2 = "select * from Punish where StudentID = '%s'"
        # 当查询结果为空时，弹窗提示
        cur.execute(sql1 % entryId.get())
        result1 = cur.fetchall()
        cur.execute(sql2 % entryId.get())
        result2 = cur.fetchall()
        if not result1 and not result2:
            messagebox.showinfo("提示", "未找到相关记录")
        for item in Tree1.get_children():
            Tree1.delete(item)
        for item in result1:
            Tree1.insert("", "end", values=(item["Detail"]))
        for item in Tree2.get_children():
            Tree2.delete(item)
        for item in result2:
            Tree2.insert("", "end", values=(item["Detail"]))

    root4 = Tk()
    root4.title("奖惩管理")
    root4.config(width=600)
    root4.config(height=600)

    button_insert_rp = Button(root4, text="录入奖惩", command=insert_rp)
    button_insert_rp.place(x=200, y=100, height=35, width=200)

    label = Label(root4, text="学号：")
    label.place(x=30, y=20, height=30, width=80)
    entryId = Entry(root4)
    entryId.place(x=110, y=20, height=30, width=500)
    button_sel_rp = Button(root4, text="查询奖惩", command=sel_rp)
    button_sel_rp.place(x=200, y=60, height=35, width=200)

    Tree1 = Treeview(root4, columns=("内容"), show="headings", height=21)
    Tree2 = Treeview(root4, columns=("内容"), show="headings", height=21)
    text1 = Label(root4, text="奖励:")
    text1.place(x=50, y=200)
    Tree1.place(x=50, y=250)
    text2 = Label(root4, text="惩罚:")
    text2.place(x=350, y=200)
    Tree2.place(x=350, y=250)

    button_del = Button(root4, text="退出", command=root4.destroy)
    button_del.place(x=200, y=140, height=35, width=200)

    root4.mainloop()


# 创建专业变更分窗口
def create_major_change():
    def sel_mc():
        sql = "select * from MajorChange where StudentID = '%s'"
        # 当查询结果为空时，弹窗提示
        cur.execute(sql % entryId.get())
        result = cur.fetchall()
        if not result:
            messagebox.showinfo("提示", "未找到相关记录")
        for item in Tree.get_children():
            Tree.delete(item)
        for item in result:
            Tree.insert("", "end", values=(item["OldMajor"], item["NewMajor"], item["ChangeDate"]))

    root5 = Tk()
    root5.title("专业变更")
    root5.config(width=600)
    root5.config(height=600)

    label = Label(root5, text="学号：")
    label.place(x=30, y=20, height=40, width=80)

    entryId = Entry(root5)
    entryId.place(x=110, y=20, height=40, width=200)
    stu_id = str(entryId.get())
    button_sel_mc = Button(root5, text="查询", command=sel_mc)
    button_sel_mc.place(x=100, y=100, height=40, width=100)
    button_del = Button(root5, text="退出", command=root5.destroy)
    button_del.place(x=250, y=100, height=40, width=100)

    Tree = Treeview(root5, columns=("原专业", "新专业", "日期"), show="headings", height=21)

    Tree.column("原专业", width=150, anchor="center")
    Tree.column("新专业", width=150, anchor="center")
    Tree.column("日期", width=150, anchor="center")
    Tree.heading("原专业", text="原专业")
    Tree.heading("新专业", text="新专业")
    Tree.heading("日期", text="日期")
    Tree.place(x=50, y=200)

    root5.mainloop()


def linkDB():
    db = pymysql.connect(host='127.0.0.1',
                         port=3306,
                         user='root',
                         passwd='733297',
                         db='student_management_system')
    cur = db.cursor(cursor=pymysql.cursors.DictCursor)
    return db, cur


db, cur = linkDB()
root = Tk()
root.title("学生信息管理系统")
root.geometry("800x600")
root.resizable(False, False)

canvas = Canvas(root, width=800, height=600, bg='white')
image = Image.open('./images/1.jpg')
im = ImageTk.PhotoImage(image)
canvas.create_image(400, 300, image=im)
canvas.pack()

button_create_stu = Button(root, text="学生信息", command=create_stu)
button_create_stu.place(x=200, y=50, height=40, width=200)

button_create_score = Button(root, text="选课及课程成绩", command=create_score)
button_create_score.place(x=200, y=150, height=40, width=200)

button_create_course = Button(root, text="课程管理", command=create_course)
button_create_course.place(x=200, y=250, height=40, width=200)

button_create_rp = Button(root, text="奖惩管理", command=create_reward_punish)
button_create_rp.place(x=200, y=350, height=40, width=200)

button_create_mc = Button(root, text="专业变更", command=create_major_change)
button_create_mc.place(x=200, y=450, height=40, width=200)
button_exit = Button(root, text="退出", command=root.destroy)
button_exit.place(x=200, y=550, height=40, width=200)

root.mainloop()
