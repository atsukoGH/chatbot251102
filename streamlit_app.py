import streamlit as st
import google.generativeai as genai

# 追加: ファイル読み取り用ライブラリ
import io
import PyPDF2
import docx

st.title("💬 Chatbot (Gemini 2.5 Pro + ファイル質問対応)")
st.write(
    "このチャットボットはGoogle Gemini 2.5 Pro APIを使って返答します。テキスト・PDF・Wordファイルをアップロードすると、５行程度で要約します"
)
# Streamlit Community CloudのSecretsからAPIキーを取得
# .streamlit/secrets.toml に GEMINI_API_KEY = "YOUR_API_KEY" を設定してください
gemini_api_key = st.secrets.get("GEMINI_API_KEY")

uploaded_file = st.file_uploader(
    "質問したいファイルをアップロードしてください（txt/pdf/docx対応）",
    type=["txt", "pdf", "docx"]
)

def extract_text_from_file(uploaded_file):
    """アップロードファイルからテキストを抽出。対応: txt, pdf, docx"""
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception:
            uploaded_file.seek(0)
            return uploaded_file.read().decode("shift-jis", errors="ignore")
    elif name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            st.error(f"PDFの読み取りでエラー: {e}")
            return None
    elif name.endswith(".docx"):
        try:
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            st.error(f"Wordファイルの読み取りでエラー: {e}")
            return None
    else:
        st.error("未対応のファイル形式です。")
        return None

if not gemini_api_key:
    st.info("続行するにはGemini APIキーをsecretsに設定してください。", icon="🗝️")
else:
    genai.configure(api_key=gemini_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "file_content" not in st.session_state:
        st.session_state.file_content = ""
    if "file_summary" not in st.session_state:
        st.session_state.file_summary = ""

    if uploaded_file is not None:
        file_content = extract_text_from_file(uploaded_file)
        st.session_state.file_content = file_content or ""
        if file_content:
            # Geminiで要約
            try:
                model = genai.GenerativeModel("gemini-2.5-pro")
                summary_prompt = (
                    "次のテキストを5行程度の日本語で簡潔に要約してください：\n\n" + file_content
                )
                response = model.generate_content(summary_prompt)
                summary = response.text.strip()
                st.session_state.file_summary = summary
                st.success("ファイルをアップロードしました！")
                st.markdown("#### ファイル内容の要約（約5行）")
                st.markdown(summary)
            except Exception as e:
                st.session_state.file_summary = f"要約中にエラーが発生しました: {e}"
                st.error(st.session_state.file_summary)
        else:
            st.session_state.file_summary = "ファイルからテキストを抽出できませんでした。"
            st.error(st.session_state.file_summary)

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
