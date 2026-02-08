import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

# ფაილების აბსოლუტური გზა
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "marge_database.json")
LOG_FILE = os.path.join(BASE_DIR, "marge_logs.json")

def load_data(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return default
    return default

def save_data(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"შეცდომა შენახვისას: {e}")

class MargeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MARGE - მართვის სისტემა")
        self.root.geometry("1200x850")
        self.root.configure(bg="#1a1a1a")
        
        # მონაცემების ჩატვირთვა
        self.db = load_data(DB_FILE, {"გორი": {"მეშაურმე": [], "მოლარე": [], "სამზარეულო": []}, 
                                      "ავტობანი": {"მეშაურმე": [], "მოლარე": [], "სამზარეულო": []}})
        self.logs = load_data(LOG_FILE, [])
        self.current_branch = None
        self.main_menu()

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    def main_menu(self):
        self.clear()
        tk.Label(self.root, text="MARGE", font=("Arial", 60, "bold"), fg="#FFC107", bg="#1a1a1a").pack(pady=50)
        f = tk.Frame(self.root, bg="#1a1a1a")
        f.pack(pady=20)
        for b in ["გორი", "ავტობანი"]:
            tk.Button(f, text=f"📍 {b}", font=("Sylfaen", 20, "bold"), width=15, bg="#d32f2f", fg="white",
                      relief="flat", cursor="hand2", command=lambda b=b: self.dashboard(b)).pack(side="left", padx=20)

    def dashboard(self, branch):
        self.current_branch = branch
        self.clear()
        sidebar = tk.Frame(self.root, bg="#262626", width=250)
        sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text=f"MARGE\n{branch}", font=("Sylfaen", 20, "bold"), fg="#FFC107", bg="#262626", pady=30).pack()
        
        menu = [("🏠 დღევანდელი ცვლა", self.show_today), ("📅 კვირის გრაფიკი", self.show_week), 
                ("⏱️ აღრიცხვა", self.show_attendance_positions), ("📈 ანალიტიკა", self.show_analytics), ("⚙️ მართვა", self.show_mgmt)]
        
        for t, c in menu:
            tk.Button(sidebar, text=t, font=("Sylfaen", 13), bg="#333", fg="white", relief="flat", anchor="w",
                      padx=20, pady=15, command=c).pack(fill="x", padx=10, pady=2)
            
        tk.Button(sidebar, text="⬅️ უკან", bg="#d32f2f", fg="white", command=self.main_menu).pack(side="bottom", fill="x", padx=10, pady=20)
        self.cont = tk.Frame(self.root, bg="#1a1a1a")
        self.cont.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.show_today()

    def show_attendance_positions(self):
        for w in self.cont.winfo_children(): w.destroy()
        tk.Label(self.cont, text="აირჩიეთ პოზიცია", font=("Sylfaen", 24, "bold"), fg="white", bg="#1a1a1a").pack(pady=30)
        grid_f = tk.Frame(self.cont, bg="#1a1a1a")
        grid_f.pack()
        for name, color in [("მეშაურმე", "#e67e22"), ("მოლარე", "#3498db"), ("სამზარეულო", "#2ecc71")]:
            tk.Button(grid_f, text=name, font=("Sylfaen", 18, "bold"), width=15, height=5,
                      bg=color, fg="white", relief="flat", cursor="hand2",
                      command=lambda p=name: self.log_delay_ui(p)).pack(side="left", padx=15)

    def log_delay_ui(self, pos):
        for w in self.cont.winfo_children(): w.destroy()
        tk.Label(self.cont, text=f"{pos} - აღრიცხვა", font=("Sylfaen", 20, "bold"), fg="white", bg="#1a1a1a").pack(pady=20)
        names = [p['name'] for p in self.db[self.current_branch][pos]]
        cb = ttk.Combobox(self.cont, values=names, font=("Sylfaen", 16), state="readonly", width=30)
        cb.pack(pady=20)
        if names: cb.current(0)
        res_lbl = tk.Label(self.cont, text="მოგესალმებით!", font=("Arial", 28, "bold"), fg="#FFC107", bg="#1a1a1a")
        res_lbl.pack(pady=40)

        def record():
            name = cb.get()
            if not name: return
            person = next(p for p in self.db[self.current_branch][pos] if p['name'] == name)
            day_geo = {"Monday":"ორშაბათი","Tuesday":"სამშაბათი","Wednesday":"ოთხშაბათი","Thursday":"ხუთშაბათი","Friday":"პარასკევი","Saturday":"შაბათი","Sunday":"კვირა"}[datetime.now().strftime("%A")]
            shift = person['schedule'].get(day_geo, "დასვენება")
            if shift == "დასვენება":
                res_lbl.config(text="დღეს დასვენებაა!", fg="#3498db")
                return
            target_time = "08:30:00" if shift == "დილა" else "17:30:00"
            now = datetime.now()
            target_dt = datetime.strptime(now.strftime("%Y-%m-%d ") + target_time, "%Y-%m-%d %H:%M:%S")
            diff = now - target_dt
            delay_str = f"{int(diff.total_seconds())//3600:02d}:{(int(diff.total_seconds())%3600)//60:02d}:{int(diff.total_seconds())%60:02d}" if diff.total_seconds() > 0 else "00:00:00"
            
            res_lbl.config(text=f"დააგვიანა: {delay_str}" if delay_str != "00:00:00" else "დროულია ✔", fg="#d32f2f" if delay_str != "00:00:00" else "#2ecc71")
            
            self.logs.append({"branch": self.current_branch, "name": name, "delay": delay_str, "date": now.strftime("%Y-%m-%d"), "pos": pos, "time": now.strftime("%H:%M:%S")})
            save_data(LOG_FILE, self.logs)

        tk.Button(self.cont, text="✅ დაფიქსირება", font=("Sylfaen", 16, "bold"), bg="#FFC107", width=20, pady=10, command=record).pack()
        tk.Button(self.cont, text="🔙 სხვა პოზიცია", bg="#333", fg="white", command=self.show_attendance_positions).pack(pady=20)

    def show_week(self):
        for w in self.cont.winfo_children(): w.destroy()
        days = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]
        for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
            tk.Label(self.cont, text=pos, bg="#d32f2f", fg="white", font=("Sylfaen", 12, "bold")).pack(fill="x", pady=(10,0))
            tree = ttk.Treeview(self.cont, columns=["სახელი"] + days, show='headings', height=4)
            tree.tag_configure('off', foreground="#ff4d4d", font=("Sylfaen", 11, "bold")) 
            tree.heading("სახელი", text="თანამშრომელი")
            for d in days: tree.heading(d, text=d); tree.column(d, width=95, anchor="center")
            tree.pack(fill="x", pady=5)
            for p in self.db[self.current_branch][pos]:
                vals = [p['name']] + [p['schedule'].get(d, "-") for d in days]
                iid = tree.insert("", "end", values=vals)
                if "დასვენება" in vals: tree.item(iid, tags=('off',))

    def show_today(self):
        for w in self.cont.winfo_children(): w.destroy()
        day_geo = {"Monday":"ორშაბათი","Tuesday":"სამშაბათი","Wednesday":"ოთხშაბათი","Thursday":"ხუთშაბათი","Friday":"პარასკევი","Saturday":"შაბათი","Sunday":"კვირა"}[datetime.now().strftime("%A")]
        tk.Label(self.cont, text=f"დღეს: {day_geo}", font=("Sylfaen", 24, "bold"), fg="white", bg="#1a1a1a").pack(pady=10)
        main_f = tk.Frame(self.cont, bg="#1a1a1a")
        main_f.pack(fill="both", expand=True)
        for shift, col in [("დილა", "#FFC107"), ("საღამო", "#d32f2f")]:
            f = tk.LabelFrame(main_f, text=shift, font=("Sylfaen", 14), fg=col, bg="#1a1a1a", labelanchor="n", pady=10)
            f.pack(side="left", fill="both", expand=True, padx=10)
            for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
                for p in self.db[self.current_branch][pos]:
                    if p['schedule'].get(day_geo) == shift:
                        tk.Label(f, text=f"{p['name']} - {pos}", font=("Sylfaen", 12), fg="white", bg="#1a1a1a").pack()

    def show_mgmt(self):
        for w in self.cont.winfo_children(): w.destroy()
        btn_f = tk.Frame(self.cont, bg="#1a1a1a")
        btn_f.pack(pady=10)
        tk.Button(btn_f, text="➕ დამატება", bg="#2ecc71", fg="white", width=15, command=lambda: self.editor()).pack(side="left", padx=5)
        tree = ttk.Treeview(self.cont, columns=("სახელი", "პოზიცია"), show='headings', height=12)
        tree.heading("სახელი", text="სახელი"); tree.heading("პოზიცია", text="პოზიცია")
        tree.pack(fill="both", expand=True, padx=20)
        for pos in self.db[self.current_branch]:
            for p in self.db[self.current_branch][pos]: tree.insert("", "end", values=(p['name'], pos))
        
        def edit():
            sel = tree.selection()
            if sel:
                n, p = tree.item(sel)['values']
                person = next((i for i in self.db[self.current_branch][p] if i['name'] == n), None)
                if person: self.editor(person, p)

        tk.Button(self.cont, text="📝 რედაქტირება", bg="#3498db", fg="white", width=20, command=edit).pack(pady=5)
        tk.Button(self.cont, text="🗑️ წაშლა", bg="#d32f2f", fg="white", width=20, command=lambda: self.del_st(tree)).pack(pady=5)

    def editor(self, edit_p=None, old_pos=None):
        win = tk.Toplevel(self.root); win.geometry("450x650"); win.grab_set()
        tk.Label(win, text="სახელი:").pack()
        en = tk.Entry(win, font=("Arial", 12)); en.pack()
        if edit_p: en.insert(0, edit_p['name'])
        ep = ttk.Combobox(win, values=["მეშაურმე", "მოლარე", "სამზარეულო"], state="readonly"); ep.pack()
        if old_pos: ep.set(old_pos)
        else: ep.current(0)
        days = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]
        sch = {}
        for d in days:
            f = tk.Frame(win); f.pack(pady=2)
            tk.Label(f, text=d, width=12).pack(side="left")
            c = ttk.Combobox(f, values=["დილა", "საღამო", "დასვენება"], width=10, state="readonly")
            c.set(edit_p['schedule'].get(d, "დილა") if edit_p else "დილა"); c.pack(); sch[d] = c
            
        def save_and_close():
            n, p = en.get(), ep.get()
            if not n: return
            if edit_p: self.db[self.current_branch][old_pos] = [i for i in self.db[self.current_branch][old_pos] if i['name'] != edit_p['name']]
            self.db[self.current_branch][p].append({"name": n, "schedule": {d: sch[d].get() for d in days}})
            save_data(DB_FILE, self.db)
            win.destroy(); self.show_mgmt()

        tk.Button(win, text="შენახვა", bg="green", fg="white", command=save_and_close, pady=10).pack(pady=20)

    def show_analytics(self):
        for w in self.cont.winfo_children(): w.destroy()
        cols = ("თარიღი", "სახელი", "დაგვიანება")
        tree = ttk.Treeview(self.cont, columns=cols, show='headings')
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)
        for l in reversed(self.logs):
            if l['branch'] == self.current_branch: tree.insert("", "end", values=(l['date'], l['name'], l['delay']))

    def del_st(self, tree):
        sel = tree.selection()
        if sel and messagebox.askyesno("!", "წავშალოთ?"):
            n, p = tree.item(sel)['values']
            self.db[self.current_branch][p] = [i for i in self.db[self.current_branch][p] if i['name'] != n]
            save_data(DB_FILE, self.db)
            self.show_mgmt()

if __name__ == "__main__":
    root = tk.Tk()
    app = MargeApp(root)
    root.mainloop()