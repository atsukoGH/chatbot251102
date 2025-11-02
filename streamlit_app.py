import streamlit as st
import requests

st.title("💬 Chatbot (Gemini API版)")
st.write(
    "このチャットボットはGoogle Gemini API（Generative Language API）を使用して応答を生成します。"
    "利用するには、Google Gemini APIキーが必要です。APIキーは[こちら](https://makersuite.google.com/app/apikey)から取得できます。"
    "元のOpenAI版のチュートリアルは[こちら](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)です。"
)

gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("APIキーを入力してください。", icon="🗝️")
else:
    # 最新エンドポイント (2025年11月現在)
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("何か話しかけてみてください！"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini API expects dialog history as a list of message dicts in the form {"role": "...", "parts": [{"text": "..."}]}
        gemini_history = []
        for m in st.session_state.messages:
            # Gemini API: role is "user" or "model"
            role = "user" if m["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {
            "contents": gemini_history
        }
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": gemini_api_key
        }

        try:
            response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            model_reply = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate:
                    parts = candidate["content"].get("parts", [])
                    if parts:
                        model_reply = parts[0].get("text", "")
            else:
                model_reply = "エラー: Geminiから有効な応答が返されませんでした。"

        except Exception as e:
            model_reply = f"エラーが発生しました: {e}"

        with st.chat_message("assistant"):
            st.markdown(model_reply)
        st.session_state.messages.append({"role": "assistant", "content": model_reply})
