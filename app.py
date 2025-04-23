import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Registro de Asistencia", layout="centered")
st.title("🔐 Registro de Asistencia con Código")

# ID de tu Google Sheet
sheet_id = "1SDlt9pr42i9N6-wV8qtEhNqzxM6nmxzAveiwD4l0m5M"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    # Cargar el archivo como DataFrame
    df = pd.read_csv(csv_url)

    if "Asistencia" not in df.columns:
        df["Asistencia"] = ""

    # Formulario de ingreso de código
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
        else:
            st.warning("❗ Código no válido. No está en la lista.")

    # Descargar Excel actualizado
    st.markdown("---")
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📥 Descargar Excel actualizado", output.getvalue(), file_name="Asistencia_actualizada.xlsx")

except Exception as e:
    st.error("❌ No se pudo cargar el archivo automáticamente.")
    st.text(f"Error técnico: {e}")
