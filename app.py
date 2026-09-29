import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# ==========================================
# 1. БЕТТІҢ БАПТАУЛАРЫ
# ==========================================
st.set_page_config(
    page_title="Enterprise WMS Pro — Қойманы Басқару Жүйесі", 
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. ДИЗАЙН ВЕЛ СТИЛЬДЕР (ADVANCED CSS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* Верхний главный баннер */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.12);
    }
    .main-header h1 {
        font-size: 30px;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF;
    }
    .main-header p {
        font-size: 14px;
        color: #94A3B8;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Карточкалар (KPI Metrics) */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        padding: 20px 22px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
    }

    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Батырмалар */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Профиль карточкасы */
    .user-profile {
        padding: 12px;
        background-color: #F1F5F9;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #CBD5E1;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ФАЙЛДАР ЖӘНЕ ДЕРЕКТЕР АҒЫНЫ (DATA ENGINE)
# ==========================================
DATA_FILE = "warehouse_data.csv"
LOG_FILE = "warehouse_logs.csv"

def init_files():
    if not os.path.exists(DATA_FILE):
        df_init = pd.DataFrame(columns=["ID", "Тауар атауы", "Категория", "Саны (шт)", "Бағасы ($)", "Жауапты тұлға"])
        df_init.to_csv(DATA_FILE, index=False)
        
    if not os.path.exists(LOG_FILE):
        logs_init = pd.DataFrame(columns=["Уақыты", "Қолданушы", "Роль", "Операция түрі", "Тауар атауы", "Өзгеріс саны", "Сипаттама"])
        logs_init.to_csv(LOG_FILE, index=False)

init_files()

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_logs():
    return pd.read_csv(LOG_FILE)

def log_action(user, role, action_type, product_name, qty_change, description):
    logs = load_logs()
    new_log = {
        "Уақыты": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Қолданушы": user,
        "Роль": role,
        "Операция түрі": action_type,
        "Тауар атауы": product_name,
        "Өзгеріс саны": qty_change,
        "Сипаттама": description
    }
    logs = pd.concat([pd.DataFrame([new_log]), logs], ignore_index=True)
    logs.to_csv(LOG_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Қойма тізімі')
    return output.getvalue()

df = load_data()

# ==========================================
# 4. АВТОРИЗАЦИЯ ЖӘНЕ РОЛЬДЕР
# ==========================================
USERS = {
    "admin": {"password": "123", "role": "Менеджер", "name": "Бекзат Әлібеков"},
    "worker": {"password": "123", "role": "Складшы", "name": "Асан Ерболұлы"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔒 WMS Жүйесіне кіру</h2>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        with st.form("login_form"):
            username = st.text_input("Логин (admin немесе worker):")
            password = st.text_input("Пароль:", type="password")
            submit_login = st.form_submit_button("Кіру", use_container_width=True)
            
            if submit_login:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_info = USERS[username]
                    st.success("Сәтті кірдіңіз!")
                    st.rerun()
                else:
                    st.error("Логин немесе пароль қате!")
    st.stop()

# ==========================================
# 5. HEADER ЖӘНЕ SIDEBAR
# ==========================================
user_data = st.session_state.user_info

st.markdown(f"""
    <div class="main-header">
        <h1>📦 Enterprise WMS Pro — Қойманы Басқару Жүйесі</h1>
        <p>Автоматтандырылған қойма аналитикасы, кіріс/шығыс есебі және оқиғалар журналы</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"""
        <div class="user-profile">
            <b>👤 Пайдаланушы:</b> {user_data['name']}<br>
            <b>🛡️ Роль:</b> {user_data['role']}
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Жүйеден шығу", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider()
    
    # Рольге байланысты меню
    menu_options = ["📊 Басқару Панелі (Dashboard)", "🔄 Қойма Операциялары (Кіріс/Шығыс)"]
    if user_data["role"] == "Менеджер":
        menu_options.extend(["➕ Жаңа Тауар Қосу", "✏️ Өңдеу & Жою", "📜 Оқиғалар Журналы (Audit Log)"])
        
    page = st.radio("Бөлімді таңдаңыз:", menu_options)

# ==========================================
# 6. БӨЛІМДЕР
# ==========================================

# ----------------- 1. DASHBOARD -----------------
if page == "📊 Басқару Панелі (Dashboard)":
    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("🔍 Іздеу (Тауар атауы немесе жауапты):", placeholder="Іздеу сөзін жазыңыз...")
    with c_filter:
        cats = ["Барлығы"] + list(df["Категория"].unique()) if not df.empty else ["Барлығы"]
        selected_cat = st.selectbox("Категория сүзгісі:", cats)

    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Тауар атауы"].str.contains(search_query, case=False, na=False) |
            filtered_df["Жауапты тұлға"].str.contains(search_query, case=False, na=False)
        ]
    if selected_cat != "Барлығы":
        filtered_df = filtered_df[filtered_df["Категория"] == selected_cat]

    st.write("")
    
    # KPI Карточкалар
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📦 Тауар позициялары", len(filtered_df))
    
    total_qty = filtered_df["Саны (шт)"].sum() if not filtered_df.empty else 0
    k2.metric("🔢 Жалпы тауар саны", f"{int(total_qty):,} шт")
    
    total_val = (filtered_df["Саны (шт)"] * filtered_df["Бағасы ($)"]).sum() if not filtered_df.empty else 0
    k3.metric("💰 Қойманың жалпы құны", f"${total_val:,.2f}")
    
    low_stock_df = filtered_df[filtered_df["Саны (шт)"] <= 5] if not filtered_df.empty else pd.DataFrame()
    k4.metric("⚠️ Таусылып жатқан (≤5 шт)", len(low_stock_df), delta_color="inverse")

    st.write("")

    if not low_stock_df.empty:
        st.error(f"🚨 **Критикалық ескерту:** {len(low_stock_df)} тауардың қоры таусылып бара жатыр! Шұғыл тапсырыс беру қажет.")

    tab1, tab2, tab3 = st.tabs(["📋 Кестелік Көрініс", "📈 ABC & Категориялық Аналитика", "⚠️ Шұғыл Тапсырыстар Тізімі"])
    
    with tab1:
        st.dataframe(filtered_df, use_container_width=True, height=380)
        if not filtered_df.empty:
            excel_data = to_excel(filtered_df)
            st.download_button(
                label="📥 Барлық деректерді Excel (.xlsx) форматында жүктеу",
                data=excel_data,
                file_name=f"WMS_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab2:
        if not filtered_df.empty:
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.caption("📊 **Категориялар бойынша сандық үлес (шт)**")
                cat_qty = filtered_df.groupby("Категория")["Саны (шт)"].sum()
                st.bar_chart(cat_qty)
                
            with chart_col2:
                st.caption("💵 **Категориялар бойынша қаржылық көлем ($)**")
                temp_df = filtered_df.copy()
                temp_df["Жалпы Құны"] = temp_df["Саны (шт)"] * temp_df["Бағасы ($)"]
                cat_val = temp_df.groupby("Категория")["Жалпы Құны"].sum()
                st.line_chart(cat_val)

            st.divider()
            st.caption("🏆 **Қоймадағы ең қымбат ТОП-5 Тауар позициясы**")
            temp_df["Жалпы Құны"] = temp_df["Саны (шт)"] * temp_df["Бағасы ($)"]
            top5 = temp_df.sort_values(by="Жалпы Құны", ascending=False).head(5)
            st.dataframe(top5[["Тауар атауы", "Категория", "Саны (шт)", "Бағасы ($)", "Жалпы Құны"]], use_container_width=True)
        else:
            st.info("Аналитика көрсету үшін мәлімет жоқ.")

    with tab3:
        if not low_stock_df.empty:
            st.dataframe(low_stock_df[["ID", "Тауар атауы", "Категория", "Саны (шт)", "Жауапты тұлға"]], use_container_width=True)
        else:
            st.success("✅ Барлық тауарлар жеткілікті мөлшерде!")

# ----------------- 2. ҚОЙМА ОПЕРАЦИЯЛАРЫ (КІРІС/ШЫҒЫС) -----------------
elif page == "🔄 Қойма Операциялары (Кіріс/Шығыс)":
    st.subheader("🔄 Тауар Түсімі мен Шығысын Тіркеу")
    
    if df.empty:
        st.info("Қоймада тауарлар жоқ.")
    else:
        col_op1, col_op2 = st.columns(2)
        
        with col_op1:
            st.markdown("### 📥 Түсім (Приход)")
            with st.form("in_form"):
                p_in_name = st.selectbox("Келіп түскен тауарды таңдаңыз:", df["Тауар атауы"].tolist(), key="in_p")
                qty_in = st.number_input("Қосылатын сан (шт):", min_value=1, value=5, step=1)
                note_in = st.text_input("Ескертпе / Жеткізуші:", value="Жеткізушінен түсті")
                btn_in = st.form_submit_button("✅ Қоймаға кірістеу")
                
                if btn_in:
                    df.loc[df["Тауар атауы"] == p_in_name, "Саны (шт)"] += qty_in
                    save_data(df)
                    log_action(user_data['name'], user_data['role'], "Түсім (Приход)", p_in_name, f"+{qty_in}", note_in)
                    st.success(f"✅ '{p_in_name}' сандары +{qty_in} данаға артты!")
                    st.rerun()

        with col_op2:
            st.markdown("### 📤 Шығыс (Расход / Сату)")
            with st.form("out_form"):
                p_out_name = st.selectbox("Жіберілетін тауарды таңдаңыз:", df["Тауар атауы"].tolist(), key="out_p")
                curr_qty = df[df["Тауар атауы"] == p_out_name]["Саны (шт)"].values[0]
                qty_out = st.number_input(f"Шығарылатын сан (Макс: {curr_qty}):", min_value=1, max_value=int(curr_qty) if curr_qty > 0 else 1, value=1, step=1)
                note_out = st.text_input("Себебі / Тапсырыс №:", value="Тапсырыс бойынша сатылды")
                btn_out = st.form_submit_button("🚨 Қоймадан шығару")
                
                if btn_out:
                    if curr_qty < qty_out:
                        st.error("Қоймада бұндай мөлшерде тауар жоқ!")
                    else:
                        df.loc[df["Тауар атауы"] == p_out_name, "Саны (шт)"] -= qty_out
                        save_data(df)
                        log_action(user_data['name'], user_data['role'], "Шығыс (Расход)", p_out_name, f"-{qty_out}", note_out)
                        st.success(f"🔴 '{p_out_name}' қоймадан -{qty_out} данаға азайды!")
                        st.rerun()

# ----------------- 3. ЖАҢА ТАУАР ҚОСУ -----------------
elif page == "➕ Жаңа Тауар Қосу" and user_data["role"] == "Менеджер":
    st.subheader("➕ Қойма номенклатурасына жаңа позиция қосу")
    
    with st.form("add_form", clear_on_submit=True):
        ca, cb = st.columns(2)
        with ca:
            name = st.text_input("Тауар атауы:", placeholder="Мысалы: Dell XPS 15")
            category = st.selectbox("Категория:", ["Электроника", "Кеңсе тауарлары", "Жиһаз", "Азық-түлік", "Басқа"])
            quantity = st.number_input("Бастапқы саны (шт):", min_value=1, value=10, step=1)
        with cb:
            price = st.number_input("Бірлігінің бағасы ($):", min_value=0.0, value=100.0, step=5.0)
            responsible = st.selectbox("Жауапты тұлға:", ["Бекзат Әлібеков (Менеджер)", "Асан Ерболұлы (Складшы)"])
            
        submit = st.form_submit_button("💾 Тауарды жүйеге тіркеу", use_container_width=True)
        if submit:
            if not name.strip():
                st.error("Тауар атауын енгізу міндетті!")
            else:
                new_id = len(df) + 1 if df.empty else int(df["ID"].max()) + 1
                new_row = {
                    "ID": new_id,
                    "Тауар атауы": name,
                    "Категория": category,
                    "Саны (шт)": quantity,
                    "Бағасы ($)": price,
                    "Жауапты тұлға": responsible
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                log_action(user_data['name'], user_data['role'], "Жаңа Тауар", name, f"+{quantity}", "Жүйеге жаңа тауар қосылды")
                st.success(f"✅ '{name}' сақталды!")

# ----------------- 4. ӨҢДЕУ & ЖОЮ -----------------
elif page == "✏️ Өңдеу & Жою" and user_data["role"] == "Менеджер":
    st.subheader("✏️ Тауар деректерін түзету немесе өшіру")
    
    if df.empty:
        st.info("Қоймада тауарлар жоқ.")
    else:
        product_name = st.selectbox("Түзететін тауарды таңдаңыз:", df["Тауар атауы"].tolist())
        selected_row = df[df["Тауар атауы"] == product_name].iloc[0]
        
        t_edit, t_del = st.tabs(["✏️ Деректерді өңдеу", "🗑️ Жою"])
        
        with t_edit:
            with st.form("edit_f"):
                cx, cy = st.columns(2)
                with cx:
                    n_name = st.text_input("Атауы:", value=selected_row["Тауар атауы"])
                    cat_list = ["Электроника", "Кеңсе тауарлары", "Жиһаз", "Азық-түлік", "Басқа"]
                    def_cat = cat_list.index(selected_row["Категория"]) if selected_row["Категория"] in cat_list else 0
                    n_cat = st.selectbox("Категория:", cat_list, index=def_cat)
                    n_qty = st.number_input("Саны (шт):", min_value=0, value=int(selected_row["Саны (шт)"]))
                with cy:
                    n_price = st.number_input("Бағасы ($):", min_value=0.0, value=float(selected_row["Бағасы ($)"]))
                    resp_list = ["Бекзат Әлібеков (Менеджер)", "Асан Ерболұлы (Складшы)"]
                    def_resp = resp_list.index(selected_row["Жауапты тұлға"]) if selected_row["Жауапты тұлға"] in resp_list else 0
                    n_resp = st.selectbox("Жауапты:", resp_list, index=def_resp)
                
                if st.form_submit_button("💾 Өзгерістерді сақтау", use_container_width=True):
                    df.loc[df["ID"] == selected_row["ID"], ["Тауар атауы", "Категория", "Саны (шт)", "Бағасы ($)", "Жауапты тұлға"]] = [n_name, n_cat, n_qty, n_price, n_resp]
                    save_data(df)
                    log_action(user_data['name'], user_data['role'], "Түзету", n_name, "0", "Деректер өңделді")
                    st.success("✅ Жаңартылды!")
                    st.rerun()

        with t_del:
            st.warning("⚠️ Өшірілген тауар қалпына келмейді!")
            if st.button("🗑️ Тауарды жүйеден өшіру", use_container_width=True):
                df = df[df["ID"] != selected_row["ID"]]
                save_data(df)
                log_action(user_data['name'], user_data['role'], "Жою", selected_row["Тауар атауы"], "0", "Тауар толығымен өшірілді")
                st.success("Өшірілді!")
                st.rerun()

# ----------------- 5. AUDIT LOG (ОҚИҒАЛАР ЖУРНАЛЫ) -----------------
elif page == "📜 Оқиғалар Журналы (Audit Log)" and user_data["role"] == "Менеджер":
    st.subheader("📜 Қоймадағы барлық әрекеттер тарихы (Audit Log)")
    logs_df = load_logs()
    
    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True)
        
        # Журналды жүктеу
        csv_logs = logs_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 Оқиғалар журналын CSV ретінде жүктеу",
            data=csv_logs,
            file_name=f"WMS_Audit_Log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Әлі ешқандай операция тіркелмеді.")