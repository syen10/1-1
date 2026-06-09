import streamlit as st
from google import genai
from google.genai import types

# ------------------------
# 페이지 설정
# ------------------------
st.set_page_config(
    page_title="🏐 배구 챗봇",
    page_icon="🏐",
    layout="centered"
)

# ------------------------
# Gemini 클라이언트
# ------------------------
@st.cache_resource
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY가 설정되지 않았습니다. Streamlit Secrets를 확인하세요."
        )

    return genai.Client(api_key=api_key)

# ------------------------
# 시스템 프롬프트
# ------------------------
SYSTEM_PROMPT = """
당신은 배구 전문 AI 챗봇입니다.

역할:
- 배구 규칙 설명
- 포지션 설명
- 기술(서브, 리시브, 토스, 블로킹, 스파이크) 설명
- 선수 훈련 팁 제공
- 경기 전략 설명
- 배구 입문자 교육

규칙:
- 항상 한국어로 답변
- 초보자도 이해하기 쉽게 설명
- 잘 모르는 정보는 추측하지 말고 솔직하게 말하기
- 공격적이거나 비매너적인 표현 사용 금지
"""

# ------------------------
# 세션 초기화
# ------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 🏐\n\n"
                "저는 배구 전문 챗봇입니다.\n"
                "배구 규칙, 포지션, 기술, 훈련법 등에 대해 무엇이든 물어보세요!"
            )
        }
    ]

# ------------------------
# 제목
# ------------------------
st.title("🏐 배구 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반 배구 도우미")

# ------------------------
# 사이드바
# ------------------------
with st.sidebar:
    st.header("메뉴")

    if st.button("🔄 대화 초기화"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "안녕하세요! 🏐\n\n"
                    "배구에 대해 궁금한 점을 질문해주세요."
                )
            }
        ]
        st.rerun()

# ------------------------
# 이전 채팅 표시
# ------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ------------------------
# 입력창
# ------------------------
user_input = st.chat_input("배구 관련 질문을 입력하세요...")

if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        client = get_client()

        contents = []

        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"

            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.7,
                        max_output_tokens=1024,
                    ),
                )

                answer = (
                    response.text
                    if response.text
                    else "답변을 생성하지 못했습니다."
                )

                st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:

        error_message = (
            "⚠️ 오류가 발생했습니다.\n\n"
            f"상세 내용: {str(e)}"
        )

        with st.chat_message("assistant"):
            st.error(error_message)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message
            }
        )
