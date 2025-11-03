import os
import streamlit as st
import base64
from openai import OpenAI

# Función para convertir la imagen en base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Configuración inicial de la página
st.set_page_config(page_title="Taylor Vision: Analiza tus imágenes", layout="centered", initial_sidebar_state="collapsed")

# Encabezado
st.title("👁️✨ Taylor Vision")
st.markdown("### Deja que **Taylor** te ayude a interpretar lo que ve en tus imágenes.")

st.caption("Sube una foto, agrega contexto si quieres... y deja que la magia ocurra 💫")

# Clave API
ke = st.text_input("🔑 Ingresa tu Clave de OpenAI")
os.environ["OPENAI_API_KEY"] = ke
api_key = os.environ["OPENAI_API_KEY"]

# Inicializar cliente OpenAI
client = OpenAI(api_key=api_key)

# Subir imagen
uploaded_file = st.file_uploader("📸 Sube una imagen (JPG, PNG o JPEG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("🖼️ Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Activar preguntas específicas
show_details = st.toggle("¿Quieres que Taylor analice algo específico?", value=False)

if show_details:
    additional_details = st.text_area(
        "✏️ Escribe aquí lo que te gustaría que Taylor analice o tenga en cuenta:",
        disabled=not show_details
    )

# Botón para analizar
analyze_button = st.button("🔍 Analizar imagen", type="secondary")

# Análisis
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("✨ Taylor está observando y pensando..."):
        # Codificar la imagen
        base64_image = encode_image(uploaded_file)

        prompt_text = "Describe lo que ves en la imagen en español, con atención al detalle."

        if show_details and additional_details:
            prompt_text += (
                f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"
            )

        # Crear solicitud
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]

        # Solicitud a OpenAI
        try:
            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.success("✨ Análisis completado por Taylor.")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    # Mensajes de advertencia
    if not uploaded_file and analyze_button:
        st.warning("📁 Por favor, sube una imagen antes de continuar.")
    if not api_key:
        st.warning("🔐 Ingresa tu clave de API para que Taylor pueda analizar la imagen.")
