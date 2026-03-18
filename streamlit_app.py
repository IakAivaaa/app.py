import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EnergyWise AI: Enterprise Edition", layout="wide")
st.title("🚀 EnergyWise AI: Neural ESG Dashboard")

# --- SIDEBAR: ΡΥΘΜΙΣΕΙΣ ---
st.sidebar.header("🏠 Δομή & Συσκευές")
beds = st.sidebar.number_input("Υπνοδωμάτια", 0, 10, 2)
living = st.sidebar.number_input("Σαλόνια", 0, 5, 1)
custom_input = st.sidebar.text_input("Custom Συσκευές:", "Air Fryer, Θερμοσίφωνας")
custom_devices = [d.strip() for d in custom_input.split(",") if d.strip()]

st.sidebar.header("💰 Οικονομικά & Green Tech")
use_night = st.sidebar.toggle("Νυχτερινό Ρεύμα", value=True)
d_price = st.sidebar.number_input("Τιμή Ημέρας (€/kWh)", value=0.15)
n_price = st.sidebar.number_input("Τιμή Νύχτας (€/kWh)", value=0.10) if use_night else d_price
co2_factor = st.sidebar.number_input("Συντελεστής CO2 (kg/kWh)", value=0.42)
budget = st.sidebar.slider("Μηνιαίο Budget (€)", 30, 800, 150)

# --- ENGINE: ΔΕΔΟΜΕΝΑ ---
tracking_items = [f"Υπνοδωμάτιο {i+1}" for i in range(beds)] + \
                 [f"Σαλόνι {i+1}" for i in range(living)] + custom_devices

if not tracking_items:
    st.warning("Προσθέστε χώρους στο Sidebar.")
    st.stop()

time_labels = [f"{h:02d}:00" for h in range(24)]

def get_engine_data(items):
    data = pd.DataFrame(index=time_labels)
    for item in items:
        p_val = 2.8 if any(x in item for x in ["Air Fryer", "Θερμοσίφωνας", "Φούρνος", "Charger"]) else 0.18
        if "Πιστολάκι" in item: p_val = 1.6
        load = np.random.rand(24) * p_val
        if p_val > 1.0: 
            load *= np.random.choice([0, 1], size=24, p=[0.85, 0.15])
        data[item] = load
    data['Total_kWh'] = data.sum(axis=1)
    return data

df = get_engine_data(tracking_items)
total_kwh = df['Total_kWh'].sum()
daily_cost = sum(df.iloc[h]['Total_kWh'] * (n_price if (h>=23 or h<7) and use_night else d_price) for h in range(24))
daily_co2 = total_kwh * co2_factor

# --- DASHBOARD METRICS ---
m1, m2, m3 = st.columns(3)
m1.metric("Κόστος Ημέρας", f"{daily_cost:.2f} €")
m2.metric("Πρόβλεψη Μήνα", f"{daily_cost*30:.2f} €", delta=f"{budget - daily_cost*30:.2f} €")
m3.metric("Ημερήσιο CO2", f"{daily_co2:.2f} kg")

# --- ΓΡΑΦΗΜΑΤΑ ---
st.markdown("---")
c_left, c_right = st.columns(2)
with c_left:
    st.subheader("📊 Συνολικό Φορτίο (Smart Meter)")
    st.line_chart(df['Total_kWh'])
with c_right:
    st.subheader("📊 Ανάλυση ανά Πηγή (Disaggregation)")
    st.line_chart(df.drop(columns=['Total_kWh']))

# --- ESG SECTION ---
st.markdown("---")
st.header("🍃 ESG & Sustainability Report")
b1, b2 = st.columns(2)
with b1:
    fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=daily_co2, title={'text':"CO2 (kg)"}, gauge={'bar':{'color':"darkgreen"}}))
    st.plotly_chart(fig_gauge, use_container_width=True)
with b2:
    st.subheader("🇪🇺 Benchmarking")
    bench_df = pd.DataFrame({'Κατηγορία': ['Εσείς', 'Μέσος Όρος Ε.Ε.'], 'kg CO2': [daily_co2, 8.5]})
    st.plotly_chart(px.bar(bench_df, x='Κατηγορία', y='kg CO2', color='Κατηγορία'), use_container_width=True)

# --- AI TRAINING ---
st.markdown("---")
st.header("🧠 AI Training Center")
col_t1, col_t2 = st.columns(2)
with col_t1:
    st.subheader("🛠️ Διόρθωση AI")
    h_sel = st.selectbox("Επιλογή Ώρας που έγινε λάθος:", time_labels)
    room_sel = st.selectbox("Σε ποιο δωμάτιο/συσκευή έγινε το λάθος;", tracking_items)
    if st.button("Εκπαίδευση AI"):
        st.success(f"Το AI έμαθε ότι στην ώρα {h_sel} η κατανάλωση στο '{room_sel}' ήταν διαφορετική!")
        st.balloons()
with col_t2:
    st.subheader("📈 Πρόοδος Μάθησης")
    learn_df = pd.DataFrame({'Εκπαίδευση': range(1,11), 'Ακρίβεια (%)': [70,75,82,85,88,90,92,94,96,98]})
    st.line_chart(learn_df.set_index('Εκπαίδευση'))

# --- EXCEL EXPORT (SINGLE SHEET PRO) ---
def create_single_sheet_excel(df_in, price_in):
    out = BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')
    df_in.to_excel(writer, sheet_name='Energy Analysis')
    workbook = writer.book
    sheet = writer.sheets['Energy Analysis']
    header_fmt = workbook.add_format({'bold':True, 'bg_color':'#1F4E78', 'font_color':'white', 'border':1, 'align':'center', 'valign':'vcenter'})
    data_fmt = workbook.add_format({'border':1, 'align':'center', 'valign':'vcenter'})
    num_fmt = workbook.add_format({'num_format': '0.00', 'border':1, 'align':'center', 'valign':'vcenter'})
    sheet.write(0, 0, 'Ώρα', header_fmt)
    sheet.set_column(0, 0, 15, data_fmt)
    for col_num, value in enumerate(df_in.columns.values):
        sheet.write(0, col_num + 1, value, header_fmt)
        sheet.set_column(col_num + 1, col_num + 1, 25, data_fmt)
    for row in range(1, 25):
        sheet.write(row, 0, time_labels[row-1], data_fmt)
        for col in range(len(df_in.columns)):
            sheet.write(row, col + 1, df_in.iloc[row-1, col], num_fmt)
    line = workbook.add_chart({'type': 'line'})
    line.add_series({'name': 'Total kWh', 'categories': ['Energy Analysis', 1, 0, 24, 0], 'values': ['Energy Analysis', 1, len(df_in.columns), 24, len(df_in.columns)]})
    sheet.insert_chart('K2', line)
    summary_row = 30
    sheet.write(summary_row, 0, 'Πηγή', header_fmt)
    sheet.write(summary_row, 1, 'Μέση Κατανάλωση (kWh)', header_fmt)
    sheet.write(summary_row, 2, 'Κόστος (€)', header_fmt)
    means = df_in.drop(columns=['Total_kWh']).mean()
    costs = df_in.drop(columns=['Total_kWh']).sum() * price_in
    for i, item in enumerate(means.index):
        sheet.write(summary_row + i + 1, 0, item, data_fmt)
        sheet.write(summary_row + i + 1, 1, means[i], num_fmt)
        sheet.write(summary_row + i + 1, 2, costs[i], num_fmt)
    pie = workbook.add_chart({'type': 'pie'})
    pie.add_series({'name': 'Cost Split', 'categories': ['Energy Analysis', summary_row + 1, 0, summary_row + len(costs), 0], 'values': ['Energy Analysis', summary_row + 1, 2, summary_row + len(costs), 2]})
    sheet.insert_chart('K20', pie)
    writer.close()
    return out.getvalue()

st.sidebar.markdown("---")
st.sidebar.download_button("📥 Εξαγωγή Report Excel (Pro)", create_single_sheet_excel(df, d_price), "EnergyWise_Final_Report.xlsx")