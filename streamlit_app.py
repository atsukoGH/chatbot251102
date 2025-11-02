import streamlit as st
import google.generativeai as genai

st.title("💬 Chatbot (Gemini 2.5 Pro + ファイル質問対応)")
st.write(
    "このチャットボットはGoogle Gemini 2.5 Pro APIを使って返答します。"
    "APIキーは[こちら](https://aistudio.google.com/app/apikey)で取得できます。"
)

gemini_api_key = st.text_input("Gemini API Key", type="password")
uploaded_file = st.file_uploader("質問したいファイルをアップロードしてください（テキストのみ対応）", type=["txt"])

if not gemini_api_key:
    st.info("続行するにはGemini APIキーを入力してください。", icon="🗝️")
else:
    genai.configure(api_key=gemini_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "file_content" not in st.session_state:
        st.session_state.file_content = ""

    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
        st.session_state.file_content = file_content
        st.success("ファイルをアップロードしました！")

    def convert_role(role):
        if role == "assistant":
            return "model"
        return role

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("ご用件を入力してください")
    if prompt:
        # ファイル内容があればプロンプトに含める
        context = ""
        if st.session_state.file_content:
            context += f"【参考ファイル内容】\n{st.session_state.file_content}\n\n"
        prompt_with_context = context + prompt

        st.session_state.messages.append({"role": "user", "content": prompt_with_context})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            chat_history = [
                {"role": convert_role(m["role"]), "parts": [m["content"]]}
                for m in st.session_state.messages
            ]
            chat = genai.GenerativeModel("gemini-2.5-pro").start_chat(history=chat_history)
            response = chat.send_message(prompt_with_context)
            reply = response.text
        except Exception as e:
            reply = f"エラーが発生しました: {e}"

        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
