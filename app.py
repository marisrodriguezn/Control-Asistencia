import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Registro de Asistencia", layout="centered")
st.title("🟢 Registro de Asistencia en Vivo")

# Cargar las credenciales desde los secrets
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

# Conectar a Google Sheets
gc = gspread.authorize(credentials)

# ID de la hoja
SPREADSHEET_ID = "1SDlt9pr42i9N6-wV8qtEhNqzxM6nmxzAveiwD4l0m5M"
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# Leer como DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Formulario para ingresar código
codigo_input = st.text_input("🔢 Ingresa tu código de 4 dígitos", max_chars=4)

if st.button("✅ Registrar asistencia") and codigo_input:
    index = df[df["Código"].astype(str) == codigo_input].index

    if not index.empty:
        i = index[0]
        if df.at[i, "Asistencia"] == "Asistió":
            st.error("🚫 Este código ya fue usado.")
        else:
            df.at[i, "Asistencia"] = "Asistió"
            nombre = df.at[i, "Nombre"]
            st.success(f"✅ Asistencia registrada para: {nombre}")
            # Actualizar celda en la hoja (i+2 por el encabezado)
            sheet.update_cell(i + 2, df.columns.get_loc("Asistencia") + 1, "Asistió")
    else:
        st.warning("❗ Código no válido. No está en la lista.")
