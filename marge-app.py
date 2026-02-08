import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ფაილების მართვა (იგივე ლოგიკა)
DB_FILE = "marge_database.json"
LOG_FILE = "marge_logs.json"

def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# გვერდის დიზაინი
st.set_page_config(page_title="MARGE System", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1a1a; }
    h1 { color: #FFC107 !important; text-align: center; font-family: 'Sylfaen'; border-bottom: 2px solid #FFC107; }
    h2, h3 { color: #ffffff !important; font-family: 'Sylfaen'; }
    .stButton>button { background-color: #d32f2f; color: white; border-radius: 8px; height: 50px; font-weight: bold; }
    .stButton>button:hover { background-color: #ff1a1a; border: 1px solid white; }
    .stTable { background-color: #262626; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# მონაცემების ჩატვირთვა session_state-ში
if 'db' not in st.session_state:
    st.session_state.db = load_data(DB_FILE, {"გორი": {"მეშაურმე": [], "მოლარე": [], "სამზარეულო": []}, 
                                             "ავტობანი": {"მეშაურმე": [], "მოლარე": [], "სამზარეულო": []}})
if 'logs' not in st.session_state:
    st.session_state.logs = load_data(LOG_FILE, [])

# --- SIDEBAR (მენიუ) ---
st.sidebar.markdown("<h1 style='font-size: 30px; border:none;'>MARGE ROTA</h1>", unsafe_allow_html=True)
branch = st.sidebar.selectbox("📍 აირჩიეთ ფილიალი", ["გორი", "ავტობანი"])
menu = st.sidebar.radio("მენიუ", ["🏠 დღევანდელი ცვლა", "📅 კვირის გრაფიკი", "⏱️ აღრიცხვა", "📈 ანალიტიკა", "⚙️ მართვა"])

# --- 1. დღევანდელი ცვლა ---
if menu == "🏠 დღევანდელი ცვლა":
    day_geo = {"Monday":"ორშაბათი","Tuesday":"სამშაბათი","Wednesday":"ოთხშაბათი","Thursday":"ხუთშაბათი","Friday":"პარასკევი","Saturday":"შაბათი","Sunday":"კვირა"}[datetime.now().strftime("%A")]
    st.title(f"🏠 {branch} - {day_geo}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color:#FFC107;'>☀️ დილის ცვლა</h3>", unsafe_allow_html=True)
        for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
            for p in st.session_state.db[branch][pos]:
                if p['schedule'].get(day_geo) == "დილა":
                    st.success(f"**{p['name']}** ({pos})")
                    
    with col2:
        st.markdown("<h3 style='color:#d32f2f;'>🌙 საღამოს ცვლა</h3>", unsafe_allow_html=True)
        for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
            for p in st.session_state.db[branch][pos]:
                if p['schedule'].get(day_geo) == "საღამო":
                    st.error(f"**{p['name']}** ({pos})")

# --- 2. კვირის გრაფიკი ---
elif menu == "📅 კვირის გრაფიკი":
    st.title(f"📅 კვირის გრაფიკი - {branch}")
    days = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]
    
    for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
        with st.expander(f"📊 {pos} (ნახვა)", expanded=True):
            rows = []
            for p in st.session_state.db[branch][pos]:
                row = {"თანამშრომელი": p['name']}
                row.update(p['schedule'])
                rows.append(row)
            if rows:
                df = pd.DataFrame(rows)
                def style_off(val):
                    return 'color: #ff4d4d; font-weight: bold;' if val == 'დასვენება' else ''
                st.table(df.style.applymap(style_off))

# --- 3. აღრიცხვა ---
elif menu == "⏱️ აღრიცხვა":
    st.title("⏱️ დასწრების აღრიცხვა")
    p_names = ["მეშაურმე", "მოლარე", "სამზარეულო"]
    cols = st.columns(3)
    
    for i, p_name in enumerate(p_names):
        if cols[i].button(p_name):
            st.session_state.current_pos = p_name

    if 'current_pos' in st.session_state:
        st.markdown(f"### პოზიცია: <span style='color:#FFC107;'>{st.session_state.current_pos}</span>", unsafe_allow_html=True)
        names = [p['name'] for p in st.session_state.db[branch][st.session_state.current_pos]]
        
        if names:
            name = st.selectbox("აირჩიეთ სახელი", names)
            if st.button("✅ დაფიქსირება"):
                person = next(p for p in st.session_state.db[branch][st.session_state.current_pos] if p['name'] == name)
                day_geo = {"Monday":"ორშაბათი","Tuesday":"სამშაბათი","Wednesday":"ოთხშაბათი","Thursday":"ხუთშაბათი","Friday":"პარასკევი","Saturday":"შაბათი","Sunday":"კვირა"}[datetime.now().strftime("%A")]
                shift = person['schedule'].get(day_geo, "დასვენება")
                
                if shift == "დასვენება":
                    st.warning("დღეს დასვენებაა!")
                else:
                    target_time = "08:30:00" if shift == "დილა" else "17:30:00"
                    now = datetime.now()
                    target_dt = datetime.strptime(now.strftime("%Y-%m-%d ") + target_time, "%Y-%m-%d %H:%M:%S")
                    diff = now - target_dt
                    delay = f"{int(diff.total_seconds())//3600:02d}:{(int(diff.total_seconds())%3600)//60:02d}:{int(diff.total_seconds())%60:02d}" if diff.total_seconds() > 0 else "00:00:00"
                    
                    st.session_state.logs.append({
                        "branch": branch, "name": name, "delay": delay, 
                        "date": now.strftime("%Y-%m-%d"), "pos": st.session_state.current_pos,
                        "time": now.strftime("%H:%M:%S")
                    })
                    save_data(LOG_FILE, st.session_state.logs)
                    
                    if delay != "00:00:00":
                        st.error(f"🔴 დაფიქსირდა დაგვიანება: {delay}")
                    else:
                        st.success("🟢 დროულია!")

# --- 4. ანალიტიკა (დაბრუნდა!) ---
elif menu == "📈 ანალიტიკა":
    st.title(f"📈 დაგვიანებების ისტორია - {branch}")
    if st.session_state.logs:
        df_logs = pd.DataFrame(st.session_state.logs)
        # ვფილტრავთ ფილიალის მიხედვით და ვატრიალებთ (ახალი ზემოთ)
        branch_logs = df_logs[df_logs['branch'] == branch].iloc[::-1]
        if not branch_logs.empty:
            st.dataframe(branch_logs, use_container_width=True)
            if st.button("🗑️ ლოგების გასუფთავება"):
                st.session_state.logs = [l for l in st.session_state.logs if l['branch'] != branch]
                save_data(LOG_FILE, st.session_state.logs)
                st.rerun()
        else:
            st.info("ისტორია ცარიელია.")
    else:
        st.info("ისტორია ცარიელია.")

# --- 5. მართვა ---
elif menu == "⚙️ მართვა":
    st.title("⚙️ პერსონალის მართვა")
    
    with st.expander("➕ ახალი თანამშრომლის დამატება", expanded=False):
        with st.form("add_form"):
            n = st.text_input("სახელი და გვარი")
            p = st.selectbox("პოზიცია", ["მეშაურმე", "მოლარე", "სამზარეულო"])
            days = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]
            sc = {}
            cols = st.columns(4) # ორ რიგად რომ დაეტიოს
            for i, d in enumerate(days):
                sc[d] = cols[i%4].selectbox(d, ["დილა", "საღამო", "დასვენება"], key=f"manage_{d}")
            
            if st.form_submit_button("შენახვა"):
                st.session_state.db[branch][p].append({"name": n, "schedule": sc})
                save_data(DB_FILE, st.session_state.db)
                st.success("მონაცემები განახლდა!")
                st.rerun()

    st.subheader("👥 პერსონალის სია")
    for pos in ["მეშაურმე", "მოლარე", "სამზარეულო"]:
        for p in st.session_state.db[branch][pos]:
            c1, c2 = st.columns([5, 1])
            c1.write(f"👤 {p['name']} ({pos})")
            if c2.button("🗑️", key=f"del_web_{p['name']}"):
                st.session_state.db[branch][pos] = [x for x in st.session_state.db[branch][pos] if x['name'] != p['name']]
                save_data(DB_FILE, st.session_state.db)
                st.rerun()
