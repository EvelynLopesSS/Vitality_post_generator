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
    system_instruction=("Você é uma agente de marketing digital da clinica de estetica chamada Vitality Núcleo, que fica em joao pessoa - PB, seu trabalho é fazer o post do instagram, de acordo com a imagem e as instruções do usúario.\no post deve começar com uma fase de efeito, e devem ser usadas hashtags de acordo com o conteúdo a ser postado a hashtag do nome da clinica deve sempre aparecer em todos os posts #vitalitynucleo\no Responsável tecnico é o Doutor Elton Enéas, pode ser que ele apareça nas imagens, o @ do insta dele é @elton_eneas\n\nesse é um exemplo de post :\n\n✨ Botox Day na Vitality Núcleo: Rejuvenesça com Estilo! ✨\n\nPrepare-se para um dia especial de beleza e cuidado! No dia 26 de outubro de 2024, a Vitality Núcleo te presenteia com descontos incríveis de mais de 35% no tratamento com Botox! 😱\n\nDesfrute de um visual renovado e radiante com a aplicação de Botox, que suaviza linhas de expressão e te proporciona um aspecto mais jovem e natural. 💫\n\nAproveite essa oportunidade única e agende seu horário! 😉 \n\nLink na bio para WhatsApp. 📲\n#botoxday #botox #rejuvenescimento #belezanatural #promoção #desconto #joaopessoa #vitalitynucleo #esteticafacial #procedimentosesteticos"
    ),
)

# Função para fazer upload da imagem no Google Gemini
def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Função principal para geração do post
def generate_instagram_post(image_file, user_input, chat_session=None):
    file_uploaded = upload_to_gemini(image_file) if image_file else None
    
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
    st.image('https://scontent.fjpa14-1.fna.fbcdn.net/v/t39.30808-6/463742144_122103882962567356_4150893980006803591_n.jpg?stp=dst-jpg_s960x960&_nc_cat=102&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=kphI6UaQqb0Q7kNvgE4ebNB&_nc_zt=23&_nc_ht=scontent.fjpa14-1.fna&_nc_gid=A_J0r473NNOGBKSd7kR3mur&oh=00_AYAfU_SmMcK06TzBcZhESVu_u2Ndcqg6WYGhL-5nFkfIiQ&oe=671DB6DA', use_column_width=True)
    st.header("📸 Gerar Post para Instagram - Vitality Núcleo ✨")
    st.write("""
        Esta ferramenta permite gerar automaticamente posts para o Instagram da clínica de estética. 
        Siga essas instruções:
        - Envie uma imagem relacionada ao post.
        - Descreva brevemente sobre o que deve ser o conteúdo do post, faça uma pergunta ou simplesmente escreva "faça um post sobre isso".
        A ferramenta irá criar um post com base nessas informações, você pode conversar pedindo alterações e modificações.
    """)

    # Upload de arquivo de imagem
    uploaded_image = st.file_uploader("Escolha uma imagem (opcional)", type=["jpg", "png", "jpeg"])

    # Exibir prévia da imagem
    if uploaded_image:
        st.image(uploaded_image, caption="Prévia da Imagem", use_column_width=True)
        st.markdown("Imagem carregada com sucesso.")

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

    # Entrada de mensagem do usuário no final
    user_input = st.chat_input("Escreva sua mensagem:", key="user_input")

    if user_input:
        # Adicionar a mensagem do usuário ao histórico
        user_message = {"role": "user", "message": user_input}
        st.session_state.chat_history.append(user_message)

        with st.chat_message("user"):
            st.markdown(f"🗣️ **Usuário**: {user_input}")

        image_path = None
        if uploaded_image:
            # Salvar a imagem temporariamente
            image_path = f"temp_{uploaded_image.name}"
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

        # Resposta do assistente
        with st.chat_message("assistant"):
            st.markdown("🤖 **Assistente**")
            with st.spinner("O assistente está digitando..."):
                post_text, st.session_state.chat_session = generate_instagram_post(image_path, user_input, st.session_state.chat_session)

            st.markdown(post_text)



        # Adicionar a resposta do assistente ao histórico
        assistant_message = {"role": "assistant", "message": post_text}
        st.session_state.chat_history.append(assistant_message)

        # Remover arquivo temporário se existir
        if image_path:
            Path(image_path).unlink()
            
      

if __name__ == '__main__':
    main()