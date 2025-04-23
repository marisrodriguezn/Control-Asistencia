import streamlit as st
import pandas as pd

st.set_page_config(page_title="Registro de Asistencia por QR", layout="centered")

st.title("📋 Registro de Asistencia")
st.markdown("Escanea el código QR del invitado o escribe el **código único** manualmente.")

# Cargar el Excel con la lista de invitados
archivo_excel = st.file_uploader("📁 Sube el archivo Excel con los códigos QR", type=["xlsx"])

if archivo_excel:
    df = pd.read_excel(archivo_excel)

    # Asegurarse de tener columna de Asistencia
    if "Asistencia" not in df.columns:
        df["Asistencia"] = ""

    codigo_input = st.text_input("🔍 Código escaneado:", placeholder="Ej. INV005")

    if st.button("✅ Registrar asistencia") and codigo_input:
        index = df[df["Código único"] == codigo_input].index

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

    # Descargar archivo actualizado
    st.markdown("---")
    st.markdown("⬇️ Descargar registro actualizado:")
    from io import BytesIO
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📥 Descargar Excel actualizado", output.getvalue(), file_name="Asistencia_actualizada.xlsx")
