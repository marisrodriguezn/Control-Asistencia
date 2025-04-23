import streamlit as st
import pandas as pd
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
from io import BytesIO
import requests

st.set_page_config(page_title="Registro de Asistencia por QR", layout="centered")
st.title("📋 Registro de Asistencia por QR")

# 📂 Cargar el Excel directamente desde GitHub (reemplaza con tu enlace RAW)
excel_url = "https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fraw.githubusercontent.com%2Fmarisrodriguezn%2FControl-Asistencia%2Frefs%2Fheads%2Fmain%2FInvitados_con_QR.xlsx&wdOrigin=BROWSELINK"

try:
    archivo_excel = BytesIO(requests.get(excel_url).content)
    df = pd.read_excel(archivo_excel)

    if "Asistencia" not in df.columns:
        df["Asistencia"] = ""

    # Escáner QR
    class QRScanner(VideoTransformerBase):
        def __init__(self):
            self.qr_code = ""

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            if bbox is not None and data:
                self.qr_code = data
                cv2.putText(img, f"QR: {data}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.rectangle(img, tuple(bbox[0][0]), tuple(bbox[0][2]), (0, 255, 0), 2)
            return img

    webrtc_ctx = webrtc_streamer(key="qr", video_transformer_factory=QRScanner)

    if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.qr_code:
        qr_code = webrtc_ctx.video_transformer.qr_code.strip()
        st.markdown(f"🔍 Código escaneado: `{qr_code}`")

        index = df[df["Código único"] == qr_code].index
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
    st.error("❌ No se pudo cargar el archivo automáticamente. Verifica que el enlace RAW sea válido.")
    st.text(f"Error técnico: {e}")
