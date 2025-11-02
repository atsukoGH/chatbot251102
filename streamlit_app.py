import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("💬 Chatbot (Gemini 2.5 Pro)")
st.write(
    "このチャットボットはGoogle Gemini 2.5 Pro APIを使って返答を生成します。"
    "利用にはGoogle AI Studioから取得できるGemini APIキーが必要です。"
    "APIキーは[こちら](https://aistudio.google.com/app/apikey)で取得できます。"
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("続行するにはGemini APIキーを入力してください。", icon="🗝️")
else:
    # Configure Gemini API client
    genai.configure(api_key=gemini_api_key)

    # セッション状態でメッセージ履歴を管理
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 既存のチャットメッセージの表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # チャット入力欄
    if prompt := st.chat_input("ご用件を入力してください"):
        # ユーザー入力を保存・表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini 2.5 Proで返答生成
        try:
            # Gemini 2.5 Pro モデル名は "gemini-2.5-pro" を利用
            chat = genai.GenerativeModel("gemini-2.5-pro").start_chat(history=[
                {"role": m["role"], "parts": [m["content"]]}
                for m in st.session_state.messages if m["role"] in ("user", "assistant")
            ])
            response = chat.send_message(prompt)
            reply = response.text
        except Exception as e:
            reply = f"エラーが発生しました: {e}"

        # 返答を表示・履歴に保存
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
