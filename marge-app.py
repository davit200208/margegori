import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import csv

# ფაილები
DB_FILE = "marge_db.json"
LOG_FILE = "marge_logs.json"

def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return default
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class MargeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MARGE - მართვის სისტემა")
        self.root.geometry("1150x800")
        self.root.configure(bg="#f8f9fa")
        
        self.db = load_data(DB_FILE, {"გორი": {"მეშაურმე": [], "მოლარე": [], "სამზარეულო": []}, 
                                      "ავტობანი": {"მეშაურმე": [], "მოლარე": [], "სამზარეულო": []}})
        self.logs = load_data(LOG_FILE, [])
        self.current_branch = None
        self.main_screen()

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    def show_logo(self, parent):
        # მუშაობს მხოლოდ PNG ფაილზე დამატებითი ბიბლიოთეკის გარეშე
        if os.path.exists("logo.png"):
            try:
                self.logo_img = tk.PhotoImage(file="logo.png").subsample(5, 5) # ზომის შემცირება
                lbl = tk.Label(parent, image=self.logo_img, bg=parent["bg"])
                lbl.pack(pady=10)
            except: pass

    def main_screen(self):
        self.clear()
        self.show_logo(self.root)
        tk.Label(self.root, text="MARGE", font=("Arial", 40, "bold"), fg="#e67e22", bg="#f8f9fa").pack()
        
        btn_frame = tk.Frame(self.root, bg="#f8f9fa")
        btn_frame.pack(pady=50)
        for branch in ["გორი", "ავტობანი"]:
            tk.Button(btn_frame, text=f"📍 {branch}", font=("Sylfaen", 18, "bold"), width=15, height=2, 
                      bg="#2c3e50", fg="white", cursor="hand2",
                      command=lambda b=branch: self.branch_dashboard(b)).pack(side="left", padx=25)

    def branch_dashboard(self, branch):
        self.current_branch = branch
        self.clear()
        
        sidebar = tk.Frame(self.root, bg="#2c3e50", width=240)
        sidebar.pack(side="left", fill="y")
        self.show_logo(sidebar)
        
        tk.Label(sidebar, text=f"MARGE\n{branch}", font=("Sylfaen", 18, "bold"), fg="white", bg="#2c3e50", pady=20).pack()

        btns = [("📋 განრიგი", self.schedule_menu), ("⏱️ აღრიცხვა", self.delay_menu),
                ("📈 ანალიტიკა", self.view_analytics), ("⚙️ მართვა", self.view_management)]

        for text, cmd in btns:
            tk.Button(sidebar, text=text, font=("Sylfaen", 12), bg="#34495e", fg="white", relief="flat", 
                      anchor="w", padx=25, pady=15, command=cmd).pack(fill="x", padx=10, pady=5)

        tk.Button(sidebar, text="⬅️ უკან", bg="#c0392b", fg="white", command=self.main_screen).pack(side="bottom", fill="x", padx=10, pady=30)

        self.container = tk.Frame(self.root, bg="white", highlightbackground="#dee2e6", highlightthickness=1)
        self.container.pack(side="right", fill="both", expand=True, padx=25, pady=25)
        self.schedule_menu()

    def schedule_menu(self):
        self.clear_container()
        tk.Label(self.container, text="აირჩიეთ პოზიცია განრიგისთვის", font=("Sylfaen", 20, "bold"), bg="white").pack(pady=20)
        for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
            tk.Button(self.container, text=pos, font=("Sylfaen", 14), width=25, pady=10, bg="#f1f2f6",
                      command=lambda p=pos: self.display_schedule(p)).pack(pady=10)

    def display_schedule(self, pos):
        self.clear_container()
        tk.Label(self.container, text=f"{pos}ების განრიგი", font=("Sylfaen", 18, "bold"), bg="white").pack(pady=15)
        cols = ("სახელი", "ორშ", "სამ", "ოთხ", "ხუთ", "პარ", "შაბ", "კვი")
        tree = ttk.Treeview(self.container, columns=cols, show='headings', height=15)
        for c in cols: tree.heading(c, text=c); tree.column(c, width=90, anchor="center")
        tree.pack(fill="both", expand=True, padx=10)
        for p in self.db[self.current_branch][pos]:
            tree.insert("", "end", values=(p['name'], *p['schedule'].values()))
        tk.Button(self.container, text="🔙 უკან", command=self.schedule_menu).pack(pady=10)

    def delay_menu(self):
        self.clear_container()
        tk.Label(self.container, text="აირჩიეთ პოზიცია აღრიცხვისთვის", font=("Sylfaen", 20, "bold"), bg="white").pack(pady=20)
        for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
            tk.Button(self.container, text=pos, font=("Sylfaen", 14), width=25, pady=10, bg="#f1f2f6",
                      command=lambda p=pos: self.log_delay_ui(p)).pack(pady=10)

    def log_delay_ui(self, pos):
        self.clear_container()
        tk.Label(self.container, text=f"{pos} - აღრიცხვა", font=("Sylfaen", 18, "bold"), bg="white").pack(pady=20)
        names = [p['name'] for p in self.db[self.current_branch][pos]]
        cb = ttk.Combobox(self.container, values=names, font=("Sylfaen", 14), state="readonly", width=30)
        cb.pack(pady=20)
        if names: cb.current(0)
        res_lbl = tk.Label(self.container, text="", font=("Arial", 18, "bold"), bg="white")
        res_lbl.pack(pady=20)

        def do_log():
            name = cb.get()
            if not name: return
            person = next(p for p in self.db[self.current_branch][pos] if p['name'] == name)
            day_geo = {"Monday":"ორშაბათი","Tuesday":"სამშაბათი","Wednesday":"ოთხშაბათი","Thursday":"ხუთშაბათი","Friday":"პარასკევი","Saturday":"შაბათი","Sunday":"კვირა"}[datetime.now().strftime("%A")]
            shift = person['schedule'][day_geo]
            if shift == "დასვენება": res_lbl.config(text="დღეს დასვენებაა!", fg="#3498db"); return
            target = "08:30:00" if shift == "დილა" else "17:30:00"
            now = datetime.now()
            diff = now - datetime.strptime(now.strftime("%Y-%m-%d ") + target, "%Y-%m-%d %H:%M:%S")
            delay = str(diff).split(".")[0] if diff.total_seconds() > 0 else "00:00:00"
            self.logs.append({"branch": self.current_branch, "name": name, "pos": pos, "delay": delay, "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M:%S")})
            save_data(LOG_FILE, self.logs)
            res_lbl.config(text=f"დაფიქსირდა: {delay}", fg="red" if delay != "00:00:00" else "green")

        tk.Button(self.container, text="⏱️ დაფიქსირება", bg="#e67e22", fg="white", font=("Sylfaen", 12, "bold"), pady=10, width=20, command=do_log).pack()
        tk.Button(self.container, text="🔙 უკან", command=self.delay_menu).pack(pady=20)

    def view_analytics(self):
        self.clear_container()
        tk.Label(self.container, text="ანალიტიკა", font=("Sylfaen", 20, "bold"), bg="white").pack(pady=10)
        cols = ("სახელი", "პოზიცია", "დაგვიანებები")
        tree = ttk.Treeview(self.container, columns=cols, show='headings')
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        summary = {}
        for l in self.logs:
            if l['branch'] == self.current_branch and l['delay'] != "00:00:00":
                n = l['name']
                summary[n] = summary.get(n, 0) + 1
        
        for pos in self.db[self.current_branch]:
            for p in self.db[self.current_branch][pos]:
                tree.insert("", "end", values=(p['name'], pos, summary.get(p['name'], 0)))

        def export():
            fn = f"Report_{self.current_branch}_{datetime.now().strftime('%Y%m%d')}.csv"
            with open(fn, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["თარიღი", "სახელი", "პოზიცია", "დაგვიანება"])
                for l in self.logs:
                    if l['branch'] == self.current_branch: w.writerow([l['date'], l['name'], l['pos'], l['delay']])
            messagebox.showinfo("Excel", f"შენახულია: {fn}")

        tk.Button(self.container, text="📥 ექსპორტი Excel (CSV)", bg="#27ae60", fg="white", command=export).pack(pady=10)

    def view_management(self):
        self.clear_container()
        tk.Label(self.container, text="მართვა", font=("Sylfaen", 20, "bold"), bg="white").pack(pady=10)
        bf = tk.Frame(self.container, bg="white")
        bf.pack(pady=10)
        tk.Button(bf, text="➕ დამატება", bg="#2ecc71", fg="white", command=lambda: self.staff_form()).pack(side="left", padx=10)
        tk.Button(bf, text="📝 რედაქტირება", bg="#3498db", fg="white", command=self.edit_staff).pack(side="left", padx=10)
        tk.Button(bf, text="🗑️ წაშლა", bg="#e74c3c", fg="white", command=self.delete_staff).pack(side="left", padx=10)

        self.m_tree = ttk.Treeview(self.container, columns=("სახელი", "პოზიცია"), show='headings', height=15)
        for c in ("სახელი", "პოზიცია"): self.m_tree.heading(c, text=c)
        self.m_tree.pack(fill="both", expand=True, padx=20, pady=10)
        for pos in self.db[self.current_branch]:
            for p in self.db[self.current_branch][pos]: self.m_tree.insert("", "end", values=(p['name'], pos))

    def staff_form(self, edit_p=None, old_pos=None):
        win = tk.Toplevel(self.root)
        win.title("ფორმა")
        win.geometry("450x650")
        tk.Label(win, text="სახელი:").pack(pady=5)
        en = tk.Entry(win, font=("Sylfaen", 12)); en.pack()
        if edit_p: en.insert(0, edit_p['name'])
        tk.Label(win, text="პოზიცია:").pack(pady=5)
        ep = ttk.Combobox(win, values=["მეშაურმე", "მოლარე", "სამზარეულო"], state="readonly"); ep.pack()
        if old_pos: ep.set(old_pos)
        days = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]
        svars = {}
        for d in days:
            f = tk.Frame(win); f.pack(pady=2)
            tk.Label(f, text=d, width=12).pack(side="left")
            c = ttk.Combobox(f, values=["დილა", "საღამო", "დასვენება"], width=10, state="readonly")
            c.set(edit_p['schedule'][d] if edit_p else "დილა"); c.pack(side="left")
            svars[d] = c
        def save():
            n, p = en.get(), ep.get()
            if n and p:
                if edit_p: self.db[self.current_branch][old_pos] = [i for i in self.db[self.current_branch][old_pos] if i['name'] != edit_p['name']]
                self.db[self.current_branch][p].append({"name": n, "schedule": {d: svars[d].get() for d in days}})
                save_data(DB_FILE, self.db); win.destroy(); self.view_management()
        tk.Button(win, text="შენახვა", bg="green", fg="white", pady=10, command=save).pack(pady=20)

    def edit_staff(self):
        s = self.m_tree.selection()
        if s: 
            n, p = self.m_tree.item(s)['values']
            self.staff_form(next(i for i in self.db[self.current_branch][p] if i['name'] == n), p)

    def delete_staff(self):
        s = self.m_tree.selection()
        if s and messagebox.askyesno("!", "წავშალოთ?"):
            n, p = self.m_tree.item(s)['values']
            self.db[self.current_branch][p] = [i for i in self.db[self.current_branch][p] if i['name'] != n]
            save_data(DB_FILE, self.db); self.view_management()

    def clear_container(self):
        for w in self.container.winfo_children(): w.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MargeApp(root)
    root.mainloop()
