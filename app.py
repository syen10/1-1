import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="연애상담 챗봇", page_icon="💌")

st.title("💌 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반. 진지한 위기 상황은 전문가 도움을 권장해요.")

SYSTEM_PROMPT = """
너는 따뜻하고 현실적인 연애상담 챗봇이다.
사용자의 감정을 먼저 공감하고, 판단하지 말고, 구체적인 다음 행동을 제안한다.
조작, 집착, 스토킹, 폭력, 자해 위험이 보이면 안전을 우선 안내한다.
전문가가 필요한 상황은 상담사, 병원, 긴급기관 도움을 권한다.
답변은 한국어로 자연스럽게 한다.
"""

def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY가 Secrets에 없습니다.")
        st.stop()
    return genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕. 어떤 연애 고민이 있어? 편하게 말해줘 💬"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("고민을 입력하세요")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        client = get_client()

        contents = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                role = "user"
            elif msg["role"] == "assistant":
                role = "model"
            else:
                continue

            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )

        with st.chat_message("assistant"):
            with st.spinner("답변을 생각하는 중..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.8,
                    ),
                )

                answer = response.text or "답변을 생성하지 못했어요. 다시 한 번 말해줄래요?"
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        error_msg = f"오류가 발생했어요: {e}"
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})

with st.sidebar:
    st.header("설정")
    if st.button("채팅 기록 초기화"):
        st.session_state.messages = [
            {"role": "assistant", "content": "채팅 기록을 초기화했어. 다시 고민을 말해줘 💬"}
        ]
        st.rerun()
