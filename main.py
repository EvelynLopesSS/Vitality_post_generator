import streamlit as st
from pathlib import Path
import google.generativeai as genai
import os
import base64
import time

# Função para carregar imagem e converter para base64
def load_image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

# Configuração do modelo e API
genai.configure(api_key=st.secrets["google"]["api_key"])

# Configuração do modelo de geração
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "Você é uma agente de marketing digital da clinica de estética chamada Vitality Núcleo, "
        "que fica em João Pessoa - PB. Seu trabalho é fazer posts para o Instagram, de acordo com "
        "as instruções e imagens fornecidas pelo usuário. O post deve começar com uma frase de efeito, "
        "usar hashtags apropriadas e sempre incluir #vitalitynucleo. O médico responsável é Dr. Elton Enéas "
        "(Instagram: @elton_eneas)."
    ),
)

# Função para fazer upload da imagem no Google Gemini
def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Função principal para geração do post
def generate_instagram_post(image_file, user_input, chat_session=None):
    file_uploaded = upload_to_gemini(image_file)
    
    if chat_session is None:
        # Começar uma nova conversa se não houver sessão ativa
        chat_session = model.start_chat(
            history=[{"role": "user", "parts": [file_uploaded, user_input]}]
        )
    else:
        # Enviar a mensagem para o chat em andamento
        chat_session.send_message(user_input)

    # Resposta gerada pelo modelo
    response = chat_session.send_message(user_input)
    return response.text, chat_session

# Inicializar estado da sessão para histórico de mensagens
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

# Interface do Streamlit
def main():
    st.image('https://scontent.fjpa14-1.fna.fbcdn.net/v/t39.30808-6/463742144_122103882962567356_4150893980006803591_n.jpg?stp=dst-jpg_s960x960&_nc_cat=102&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=kphI6UaQqb0Q7kNvgE4ebNB&_nc_zt=23&_nc_ht=scontent.fjpa14-1.fna&_nc_gid=A_J0r473NNOGBKSd7kR3mur&oh=00_AYAfU_SmMcK06TzBcZhESVu_u2Ndcqg6WYGhL-5nFkfIiQ&oe=671DB6DA', use_column_width=True)  # Substitua com a URL da imagem que deseja exibir
    st.header("📸 Gerar Post para Instagram - Vitality Núcleo ✨")
    st.write("""
        Esta ferramenta permite gerar automaticamente posts para o Instagram da clínica de estética. 
        Siga essas instruções:
        - Envie uma imagem relacionada ao post.
        - Descreva brevemente o post ou faça uma pergunta.
        A ferramenta irá criar um post com base nessas informações.
    """)

    # Layout geral: lado esquerdo (upload) e lado direito (chat)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Upload de Imagem")

        # Upload de arquivo de imagem
        uploaded_image = st.file_uploader("Escolha uma imagem", type=["jpg", "png", "jpeg"])
        
        # Exibir prévia da imagem
        if uploaded_image:
            st.image(uploaded_image, caption="Prévia da Imagem", use_column_width=True)
            st.markdown("Imagem carregada com sucesso.")

    with col2:
        st.header("Instruções")
        st.markdown("""
        **Como usar esta aplicação:**
        - Faça upload da imagem à esquerda.
        - Digite uma mensagem no campo abaixo para conversar com o assistente.
        """)
        
        # Exibir histórico de mensagens
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                # Estilo para mensagens do usuário
                with st.chat_message("user"):
                    st.markdown(f"🗣️ **Usuário**: {message['message']}")
            else:
                # Estilo para mensagens do assistente
                with st.chat_message("assistant"):
                    st.markdown(f"🤖 **Assistente**: {message['message']}")

        # Entrada de mensagem do usuário
        user_input = st.chat_input("Escreva sua mensagem:", key="user_input")

        if user_input and uploaded_image:
            # Salvar a imagem temporariamente
            image_path = f"temp_{uploaded_image.name}"
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            # Adicionar a mensagem do usuário ao histórico
            user_message = {"role": "user", "message": user_input}
            st.session_state.chat_history.append(user_message)
            
            with st.chat_message("user"):
                st.markdown(f"🗣️ **Usuário**: {user_input}")
            
            # Resposta do assistente
            with st.chat_message("assistant"):
                st.markdown("🤖 **Assistente**")
                with st.spinner("O assistente está digitando..."):
                    post_text, st.session_state.chat_session = generate_instagram_post(image_path, user_input, st.session_state.chat_session)
                
                st.markdown(post_text)
            
            # Adicionar a resposta do assistente ao histórico
            assistant_message = {"role": "assistant", "message": post_text}
            st.session_state.chat_history.append(assistant_message)

            # Remover arquivo temporário
            Path(image_path).unlink()

if __name__ == '__main__':
    main()
