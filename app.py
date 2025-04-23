import streamlit as st
import pandas as pd
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
from pyzbar.pyzbar import decode
from io import BytesIO

st.set_page_config(page_title="Registro de Asistencia por QR", layout="centered")
st.title("📋 Registro de Asistencia por QR")

archivo_excel = st.file_uploader("📁 Sube el archivo Excel con los códigos QR", type=["xlsx"])

# Variable global para guardar el QR detectado
qr_detectado = st.empty()

class QRScanner(VideoTransformerBase):
    def __init__(self):
        self.qr_code = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        decoded = decode(img)
        for obj in decoded:
            self.qr_code = obj.data.decode("utf-8")
            cv2.rectangle(img, (obj.rect.left, obj.rect.top),
                          (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                          (0, 255, 0), 2)
        return img

if archivo_excel:
    df = pd.read_excel(archivo_excel)

    if "Asistencia" not in df.columns:
        df["Asistencia"] = ""

    st.markdown("### 📷 Escanear QR")
    webrtc_ctx = webrtc_streamer(key="qr", video_transformer_factory=QRScanner)

    if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.qr_code:
        qr_code = webrtc_ctx.video_transformer.qr_code
        qr_detectado.text(f"🔍 Código escaneado: {qr_code}")

        # Buscar en el DataFrame
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

    # Opción para descargar lista actualizada
    st.markdown("---")
    st.markdown("⬇️ Descargar Excel actualizado con asistencia:")
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📥 Descargar Excel", output.getvalue(), file_name="Asistencia_actualizada.xlsx")
