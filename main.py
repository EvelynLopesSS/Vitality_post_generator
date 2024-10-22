import streamlit as st
from pathlib import Path
import google.generativeai as genai
import os

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

# Interface do Streamlit
def main():
    st.header("📸 ChatBot Gerador de Post - Vitality Núcleo ✨")

    # Variável para armazenar o histórico da conversa na sessão do Streamlit
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = None

    uploaded_file = st.file_uploader("Envie uma imagem", type=["png", "jpg", "jpeg"])
    user_input = st.text_input("Digite sua mensagem")

    if st.button("Enviar"):
        if uploaded_file and user_input:
            # Salvar a imagem temporariamente
            image_path = f"temp_{uploaded_file.name}"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Gerar o post e iniciar a sessão de chat
            with st.spinner('Gerando resposta...'):
                post_text, chat_session = generate_instagram_post(image_path, user_input, st.session_state.chat_session)
                
                # Atualizar o histórico com a resposta gerada
                st.session_state.chat_history.append({"role": "user", "message": user_input})
                st.session_state.chat_history.append({"role": "model", "message": post_text})
                
                # Salvar a sessão de chat
                st.session_state.chat_session = chat_session

                # Remover arquivo temporário
                Path(image_path).unlink()
        else:
            st.warning("Por favor, envie uma imagem e insira a descrição.")

    # Exibir o chat como uma conversa
    if st.session_state.chat_history:
        st.write("---")
        st.subheader("Conversa:")
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.write(f"**Você**: {msg['message']}")
            else:
                st.write(f"**Bot**: {msg['message']}")

    # Continuar a conversa
    if st.session_state.chat_session:
        modification_request = st.text_input("Pedir modificação ou continuar conversa", key="modification_input")

        if st.button("Continuar"):
            if modification_request:
                with st.spinner('Gerando nova versão...'):
                    # Adicionar a nova solicitação ao histórico
                    st.session_state.chat_history.append({"role": "user", "message": modification_request})
                    
                    # Gerar uma nova resposta levando em conta o histórico anterior
                    complete_history = [{"role": "user", "parts": [msg["message"]]} if msg["role"] == "user"
                                        else {"role": "model", "parts": [msg["message"]]}
                                        for msg in st.session_state.chat_history]
                    
                    chat_session = model.start_chat(history=complete_history)
                    response = chat_session.send_message(modification_request)
                    
                    # Atualizar o histórico com a resposta gerada
                    st.session_state.chat_history.append({"role": "model", "message": response.text})
                    
                    st.subheader("Texto Modificado:")
                    st.write(response.text)
            else:
                st.warning("Insira uma solicitação de modificação.")

if __name__ == '__main__':
    main()
