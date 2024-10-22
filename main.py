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
        "Você é uma agente de marketing digital da clínica de estética chamada Vitality Núcleo, "
        "que fica em João Pessoa - PB. Seu trabalho é fazer o post do Instagram, de acordo com a imagem e as instruções do usuário. "
        "O post deve começar com uma frase de efeito, e devem ser usadas hashtags de acordo com o conteúdo a ser postado. "
        "A hashtag do nome da clínica deve sempre aparecer em todos os posts: #vitalitynucleo. "
        "O responsável técnico é o Doutor Elton Enéas, que pode aparecer nas imagens, o @ do insta dele é @elton_eneas.\n\n"
        "Esse é um exemplo de post:\n\n"
        "✨ Botox Day na Vitality Núcleo: Rejuvenesça com Estilo! ✨\n"
        "Prepare-se para um dia especial de beleza e cuidado! No dia 26 de outubro de 2024, a Vitality Núcleo te presenteia "
        "com descontos incríveis de mais de 35% no tratamento com Botox! 😱\n\n"
        "Desfrute de um visual renovado e radiante com a aplicação de Botox, que suaviza linhas de expressão e te proporciona "
        "um aspecto mais jovem e natural. 💫\n\n"
        "Aproveite essa oportunidade única e agende seu horário! 😉 \n"
        "Link na bio para WhatsApp. 📲\n"
        "#botoxday #botox #rejuvenescimento #belezanatural #promoção #desconto #joaopessoa #vitalitynucleo #esteticafacial #procedimentosesteticos"
    ),
)

# Função para fazer upload da imagem no Google Gemini
def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Função principal para geração do post
def generate_instagram_post(image_file, user_input, chat_session=None):
    file_uploaded = upload_to_gemini(image_file) if image_file else None

    # Inicializa o histórico do chat com a mensagem do usuário
    user_message = user_input
    history = [{"role": "user", "parts": [user_message]}]

    if file_uploaded:
        # Adiciona a imagem ao histórico se foi carregada
        history.insert(0, {"role": "user", "parts": [file_uploaded]})

    if chat_session is None:
        # Começar uma nova conversa se não houver sessão ativa
        chat_session = model.start_chat(history=history)
    else:
        # Enviar a mensagem para o chat em andamento
        chat_session.send_message(user_message)

    # Resposta gerada pelo modelo
    response = chat_session.send_message(user_message)
    return response.text, chat_session

# Inicializar estado da sessão para histórico de mensagens
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

# Interface do Streamlit
def main():
    st.image('https://scontent.fjpa14-1.fna.fbcdn.net/v/t39.30808-6/463742144_122103882962567356_4150893980006803591_n.jpg?stp=dst-jpg_s960x960&_nc_cat=102&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=kphI6UaQqb0Q7kNvgE4ebNB&_nc_zt=23&_nc_ht=scontent.fjpa14-1.fna&_nc_gid=A_J0r473NNOGBKSd7kR3mur&oh=00_AYAfU_SmMcK06TzBcZhESVu_u2Ndcqg6WYGhL-5nFkfIiQ&oe=671DB6DA', use_column_width=True)
    st.header("📸 Gerar Post para Instagram - Vitality Núcleo ✨")
    st.write("""
        Esta ferramenta permite gerar automaticamente posts para o Instagram da clínica de estética. 
        Suba uma imagem e escreva suas instruções para criar um post incrível!
    """)

    image_file = st.file_uploader("Escolha uma imagem...", type=["jpg", "jpeg", "png"])
    user_input = st.text_area("Instruções do usuário", height=200)

    if st.button("Gerar Post"):
        if user_input:
            post_text, st.session_state.chat_session = generate_instagram_post(image_file, user_input, st.session_state.chat_session)
            st.markdown(post_text)
        else:
            st.warning("Por favor, insira suas instruções para gerar o post.")

if __name__ == '__main__':
    main()
