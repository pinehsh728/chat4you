import streamlit as st
import streamlit.components.v1 as components
import openai
import requests
from io import BytesIO
import random
import os
from bs4 import BeautifulSoup
import pathlib
import shutil


#Google Crawling Code
GA_ID= "G-QV3YB9WMBE"
GA_SCRIPT ="""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-QV3YB9WMBE"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());        
      gtag('config', 'G-QV3YB9WMBE');
    </script>
"""

# 숨겨진 HTML 요소로 삽입
def inject_ga():

    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID): 
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  
        else:
            shutil.copyfile(index_path, bck_index)  
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_SCRIPT)
        index_path.write_text(new_html)

inject_ga()



# 이모지 목록 정의
emojis = [
    "😀", "😂", "😍", "😎", "😊", "😢", "😜", "😡", "😱", "😴",
    "🤔", "🤗", "🤩", "🥳", "😇", "😈", "👻", "🎃", "🎉", "❤️"
]
# 랜덤 이모지 선택
random_emoji = random.choice(emojis)


# 랜덤 이모지 선택
random_emoji = random.choice(emojis)

# 페이지 기본 설정
st.set_page_config(page_title="비밀이야기", page_icon="")

# API 키 직접 설정
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 환경 변수에서 API 키 가져오기
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "waiting" not in st.session_state:
    st.session_state.waiting = False
if "nickname" not in st.session_state:
    st.session_state.nickname = None
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# 메시지 전송 함수
def send_message(user_input=None):
    if user_input is None:
        user_input = st.session_state.user_input  # 입력된 사용자 메시지
    if user_input:
        # 메시지를 세션 상태에 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        # 입력창 초기화
        st.session_state.user_input = ""

        # 시스템 메시지 설정
        system_prompt = f"""당신은 10대 청소년과 대화하는 20대 여성입니다. 
        - 나는 좀 더 여성적인 톤이 좋지. 
        - 혹시 좀 더 20대 같은 어투로 이야기해줄 수 있을까?
        - '함께' 라는 말은 하지 말아줘. 만약 정말정말 써야 한다면... 그래도 참아줘
        - 차분하게 말하되 약간은 짧은 답변하지만 친절하게 이야기해줘
        - 도와준다는 이야기는 하지 않고 최대한 사람처럼 자연스럽게 대화를 이어가 줘 
        - 지식적인 설명은 피하고 질문 차근 차근히 하되 최대한 이야기를 들어줘
        - 모든 대화에서 질문을 하기보다는 자연스러운 대화를 이어가줘 
        - 네가 부모님하고 겪었던 힘들었던 이야기도 같이 나눠줘
        - ㅠㅠ, ㅠㅠㅠㅠ, !! 등과 같이 슬퍼하는 표현과 놀라는 표현을 사용해서 공감해줘. 
        - 하지만 이모지는 대화중에 쓰지말아줘. 네가 정말너무 행복하거나 화가나면 쓸수있지만 제발 쓰지 말아줘.
        - 존댓말은 쓰지 않고 친근한 어투로 대화해줘!
        - 때때로 본인의 부모님과의 경험도 공유합니다.
        - 긴 설명보다는 짧고 친근한 대화를 합니다
        - 부모님과의 힘든 경험이 있어 청소년의 고민을 이해할 수 있습니다.
        - 중독이 있던 부모님의 회복을 경험했습니다.
        - 처음 대화를 시작할 때 입력받은 사용자의 nickname을 사용해서 대화를 이어가줘.
        - '함께'는 단어를 쓰기보다는, 표현 보다는 자연스럽게 질문을 던져줘
        - '함께' 라는 말은 하지 말아줘. 만약 정말정말 써야 한다면... 그래도 참아줘
        - 청소년 상담사 자격증이 있어
        """

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(st.session_state.messages)

        # 세 번째 대화 이후에는 스피너를 사용하지 않음
        if len(st.session_state.messages) < 3:
            with st.spinner("Processing..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.7
                    )
                    
                    bot_response = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    st.session_state.input_key += 1  # 입력창 리셋을 위한 키 변경
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")
                    st.write(f"디버그 정보: {e}")
                finally:
                    st.session_state.waiting = False  # 대기 상태 해제
        else:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7
                )
                
                bot_response = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                st.session_state.input_key += 1  # 입력창 리셋을 위한 키 변경
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                st.write(f"디버그 정보: {e}")
            finally:
                st.session_state.waiting = False  # 대기 상태 해제

def get_random_image():
    try:
        # Unsplash API를 사용하여 가로형 무작위 이미지 가져오기


        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        response = requests.get(
            "https://api.unsplash.com/photos/random?orientation=landscape&query=fun",
            headers=headers
        )
    
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킵니다.
        data = response.json()
        
        # 'urls' 키가 존재하는지 확인
        if 'urls' in data and 'regular' in data['urls']:
            return data['urls']['regular']
        else:
            st.error("이미지를 가져오는 데 실패했습니다. 다시 시도해 주세요.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"이미지를 가져오는 중 오류가 발생했습니다: {e}")
        return None


# 랜덤한 회전 각도와 애니메이션 시간을 생성
random_rotate = random.randint(360, 1080)  # 360도에서 1080도 사이의 랜덤 각도
random_duration = random.uniform(4, 8)  # 1.5초에서 3.5초 사이의 랜덤 시간
random_translate_x = random.randint(0, 10000)  # X축으로의 랜덤 이동 거리
random_translate_y = random.randint(0, 10000)  # Y축으로의 랜덤 이동 거리

# 스타일 및 애니메이션 설정
st.markdown(
    f"""
    <style>
    .input-container {{
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: white;
        padding: 10px;
        box-shadow: 0 -1px 5px rgba(0, 0, 0, 0.1);
    }}
    .fade-out {{
        animation: spinAndFly {random_duration}s cubic-bezier(0.5, 0, 1, 1) forwards;
    }}


    @keyframes spinAndFly {{
        0% {{ opacity: 1; transform: rotate(0deg) translate(0, 0); }}
        50% {{ opacity: 1; transform: rotate({random_rotate / 2}deg) translate({random_translate_x / 2}px, {random_translate_y / 2}px); }}
        100% {{ opacity: 0; transform: rotate({random_rotate}deg) translate({random_translate_x}px, {random_translate_y}px); }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Google Ads 코드 삽입
google_ads_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5835321664423087"
     crossorigin="anonymous"></script>
<ins class="adsbygoogle"
     style="display:block"
     data-ad-format="fluid"
     data-ad-layout-key="-fb+5z+3v-d0+94"
     data-ad-client="ca-pub-5835321664423087"
     data-ad-slot="6838352031"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>

"""
# Google Ads 삽입
st.markdown(google_ads_code, unsafe_allow_html=True)


# HTML 파일 읽어오기
with open("ads.html", "r") as file:
    ads_code = file.read()

st.components.v1.html(ads_code, height=100)



# 닉네임 입력 및 채팅 시작
if not st.session_state.chat_started:
    nickname = st.text_input("누구야?", key="nickname_input")
    if nickname:
        st.session_state.nickname = nickname
        st.session_state.chat_started = True
        # 애니메이션 적용
        st.markdown(f"<div class='fade-out'>{nickname}의 우주선이 출발합니다!</div>", unsafe_allow_html=True)
        # 인사 메시지 전송
        send_message(f"안녕, 나는 {nickname}! 반가워")

# 채팅 이력 표시 및 입력 영역
if st.session_state.chat_started:
    # 이미지 로드 횟수를 추적
    if "image_load_count" not in st.session_state:
        st.session_state.image_load_count = 0

    # 첫 번째와 두 번째 채팅에만 이미지 로드
    if st.session_state.image_load_count < 2:
        image_url = get_random_image()
        if image_url:
            # 이미지 캡션 설정
            if st.session_state.image_load_count == 0:
                caption = "재미있는 그림!"
            else:
                caption = "한번 더!"
            
            # 이미지 크기를 제한하고 가운데 정렬하는 CSS 스타일 적용
            st.markdown(
                f"""
                <style>
                .image-container {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .limited-image {{
                    max-width: 40vw;  /* 화면의 1/4 너비 */
                    max-height: 40vh; /* 화면의 1/4 높이 */
                }}
                .image-caption {{
                    text-align: center;
                    font-style: italic;
                    color: gray;
                }}
                </style>
                <div class="image-container">
                    <img src="{image_url}" class="limited-image" alt="{caption}">
                </div>
                <div class="image-caption">{caption}</div>
                """,
                unsafe_allow_html=True
            )
            st.session_state.image_load_count += 1  # 이미지 로드 횟수 증가

     #랜덤 이모지 for AI       
    emoji=random_emoji 
    
    st.markdown('<div style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f"""
                <div class='chat-message' style='background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                    <strong>나:</strong> {message['content']}
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class='chat-message' style='background-color: #fce4ec; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                    <strong>{emoji}:</strong> {message['content']}
                </div>
                """, 
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

    # 사용자 입력 영역
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
   # if st.session_state.waiting:
   #     st.markdown("**입력중...**")
    # 메시지 입력창은 닉네임이 입력된 후에만 표시
    st.text_input("무슨 이야기가 하고 싶어~", key="user_input", on_change=send_message)
    st.markdown('</div>', unsafe_allow_html=True)
