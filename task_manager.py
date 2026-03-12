import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os

TASK_FILE = os.path.expanduser("~/tasks.json")

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("任务四象限管理器")
        self.root.geometry("900x600")

        self.tasks = self.load_tasks()
        self.drag_data = {"widget": None, "x": 0, "y": 0}

        # 四个象限标签
        self.quadrants = {
            "紧急且重要": tk.Frame(root, bd=2, relief="ridge", bg="#ffcccc"),
            "重要不紧急": tk.Frame(root, bd=2, relief="ridge", bg="#ccffcc"),
            "紧急不重要": tk.Frame(root, bd=2, relief="ridge", bg="#ccccff"),
            "不紧急不重要": tk.Frame(root, bd=2, relief="ridge", bg="#f0f0f0"),
        }

        # 坐标布局（2x2）
        self.quadrants["紧急且重要"].grid(row=0, column=0, sticky="nsew")
        self.quadrants["重要不紧急"].grid(row=0, column=1, sticky="nsew")
        self.quadrants["紧急不重要"].grid(row=1, column=0, sticky="nsew")
        self.quadrants["不紧急不重要"].grid(row=1, column=1, sticky="nsew")

        for i in range(2):
            root.grid_columnconfigure(i, weight=1)
            root.grid_rowconfigure(i, weight=1)

        # 输入区
        input_frame = tk.Frame(root)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        tk.Label(input_frame, text="任务:").pack(side="left")
        self.task_entry = tk.Entry(input_frame, width=30)
        self.task_entry.pack(side="left", padx=5)
        tk.Label(input_frame, text="截止日期(MM-DD):").pack(side="left")
        self.ddl_entry = tk.Entry(input_frame, width=10)
        self.ddl_entry.pack(side="left", padx=5)
        tk.Label(input_frame, text="标签(#tag):").pack(side="left")
        self.tag_entry = tk.Entry(input_frame, width=10)
        self.tag_entry.pack(side="left", padx=5)
        tk.Label(input_frame, text="类别:").pack(side="left")
        self.category_var = tk.StringVar(value="紧急且重要")
        tk.OptionMenu(input_frame, self.category_var, *self.quadrants.keys()).pack(side="left", padx=5)
        tk.Button(input_frame, text="添加任务", command=self.add_task).pack(side="left", padx=5)

        self.display_tasks()
    def calculate_days_left(self, ddl):
        if not ddl:
            return None
        try:
            now = datetime.now()
            year = now.year
            ddl_date = datetime.strptime(f"{year}-{ddl}", "%Y-%m-%d")
            if ddl_date < now:
                return False
            #delta = (ddl_date - now).days
            return True
        except ValueError:
            return None
    def add_task(self):
        name = self.task_entry.get().strip()
        ddl = self.ddl_entry.get().strip()
        tag = self.tag_entry.get().strip()
        category = self.category_var.get()

        if not name:
            messagebox.showwarning("警告", "请输入任务名称")
            return
        if ddl:
            try:
                datetime.strptime(ddl, "%m-%d")
            except ValueError:
                messagebox.showwarning("格式错误", "截止日期格式应为 MM-DD")
                return

        task = {"name": name, "ddl": ddl, "tag": tag, "category": category, "done": False}
        self.tasks.append(task)
        self.save_tasks()
        self.task_entry.delete(0, tk.END)
        self.ddl_entry.delete(0, tk.END)
        self.tag_entry.delete(0, tk.END)
        self.display_tasks()

    def display_tasks(self):
        for frame in self.quadrants.values():
            for widget in frame.winfo_children():
                widget.destroy()

        for cat, frame in self.quadrants.items():
            tk.Label(frame, text=cat, bg=frame.cget("bg"), font=("Arial", 14, "bold")).pack(pady=5)
            has_task = False
            #Time_left = self.calculate_days_left(self, ddl=task['ddl'])
            for task in self.tasks:
                #if Time_left == True:
                    #now = datetime.now()
                    #year = now.year
                    #ddl_date = datetime.strptime(f"{year}-{ddl}", "%Y-%m-%d")
                    #delta = (ddl_date - now).days
                if task["category"] == cat and not task.get("done", False):
                    has_task = True
                    text = f"{task['tag']}\n{task['name']}\nDDL: {task['ddl'] or '无'}"
                    # 任务文字
                    label_frame = tk.Frame(frame, bd=1, relief="solid", bg="white")
                    label_frame.pack(fill="x", padx=5, pady=3)

                    # 勾选完成
                    var = tk.BooleanVar()
                    chk = tk.Checkbutton(label_frame, variable=var, command=lambda t=task, v=var: self.mark_done(t, v))
                    chk.pack(side="left")
                    lbl = tk.Label(label_frame, text=text, wraplength=180, justify="left", bg="white")
                    lbl.pack(side="left", padx=5)

                    # 移动任务下拉框
                    move_var = tk.StringVar(value=task["category"])
                    move_box = tk.OptionMenu(label_frame, move_var, *self.quadrants.keys(), command=lambda val, t=task: self.move_task(t, val))
                    move_box.pack(side="right")

            if not has_task:
                tk.Label(frame, text="(无任务)", bg=frame.cget("bg"), fg="gray").pack(pady=10)

    def mark_done(self, task, var):
        if var.get():
            task["done"] = True
            self.save_tasks()
            self.display_tasks()

    def move_task(self, task, new_cat):
        task["category"] = new_cat
        self.save_tasks()
        self.display_tasks()

    def save_tasks(self):
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if not os.path.exists(TASK_FILE):
            return []
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()