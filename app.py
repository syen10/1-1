import streamlit as st
from google import genai
from google.genai import types

# 페이지 설정
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Chatbot")
st.caption("Powered by Gemini 2.5 Flash Lite")

# API Key 확인
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "GEMINI_API_KEY가 설정되지 않았습니다. "
        "Streamlit Secrets를 확인하세요."
    )
    st.stop()

# Gemini 클라이언트 생성
client = genai.Client(api_key=api_key)

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! AI에 대해 무엇이든 물어보세요."
        }
    ]

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
prompt = st.chat_input("메시지를 입력하세요...")

if prompt:
    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("생각 중..."):

                # Gemini 형식으로 변환
                contents = []

                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        contents.append(
                            types.Content(
                                role="user",
                                parts=[types.Part(text=msg["content"])]
                            )
                        )
                    elif msg["role"] == "assistant":
                        contents.append(
                            types.Content(
                                role="model",
                                parts=[types.Part(text=msg["content"])]
                            )
                        )

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=contents
                )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

        except Exception as e:
            error_msg = f"오류가 발생했습니다: {str(e)}"

            st.error(error_msg)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_msg
                }
            )

# 사이드바
with st.sidebar:
    st.header("설정")

    if st.button("대화 초기화"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "안녕하세요! AI에 대해 무엇이든 물어보세요."
            }
        ]
        st.rerun()

    st.info(
        "이 챗봇은 Gemini 2.5 Flash Lite를 사용합니다."
    )
