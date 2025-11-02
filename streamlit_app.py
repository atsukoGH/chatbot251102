import streamlit as st
import requests

# Show title and description.
st.title("💬 Chatbot (Gemini API版)")
st.write(
    "このチャットボットはGoogle Gemini API（Generative Language API）を使用して応答を生成します。"
    "利用するには、Google Gemini APIキーが必要です。APIキーは[こちら](https://makersuite.google.com/app/apikey)から取得できます。"
    "元のOpenAI版のチュートリアルは[こちら](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)です。"
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("APIキーを入力してください。", icon="🗝️")
else:
    # Gemini API endpoint
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field.
    if prompt := st.chat_input("何か話しかけてみてください！"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini API expects dialog history as a list of message dicts.
        gemini_history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                gemini_history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                gemini_history.append({"role": "model", "parts": [m["content"]]})

        # Prepare the API payload.
        payload = {
            "contents": gemini_history
        }
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": gemini_api_key
        }

        # Call the Gemini API.
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Extract the model's reply.
            model_reply = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts:
                    model_reply = parts[0].get("text", "")
            else:
                model_reply = "エラー: Geminiから有効な応答が返されませんでした。"

        except Exception as e:
            model_reply = f"エラーが発生しました: {e}"

        # Stream the response and store it.
        with st.chat_message("assistant"):
            st.markdown(model_reply)
        st.session_state.messages.append({"role": "assistant", "content": model_reply})
