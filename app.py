


import streamlit as st
import requests
import xml.etree.ElementTree as ET
import re
from collections import defaultdict
import time
from difflib import get_close_matches

# 페이지 설정 - 타이틀과 레이아웃 설정
st.set_page_config(
    page_title="도서 기록장",
    page_icon="📚",
    layout="wide"
)

# API 키와 기본 URL 설정
API_KEY = "a4b364bf3e4b5c50bd807e440b289a964d31106411bce465f3fb7696e8c02dd6"
API_BASE_URL = "https://www.nl.go.kr/NL/search/openApi/search.do"

# 한국십진분류법(KDC) 코드를 카테고리 이름으로 바꾸는 함수
def get_category_name(call_no, title="", author="", search_title=""):
    """
    분류 코드를 보고 어떤 분야인지 알려주는 함수
    call_no가 없을 때는 제목, 작가, 검색어를 활용하여 스마트하게 분류
    예: "813.6" -> "한국문학"
    """
    # call_no가 있으면 우선 사용
    if call_no and call_no.strip():
        # 분류 코드에서 숫자 부분만 가져오기 (예: "813.6" -> 813)
        try:
            # 공백 제거 및 점(.) 앞의 숫자만 가져오기
            call_no_clean = call_no.strip()
            # 숫자가 아닌 문자 제거 (예: "813.6-K14" -> "813.6")
            match = re.match(r'(\d+)', call_no_clean)
            if match:
                main_code = match.group(1)
                code_num = int(main_code)
            else:
                raise ValueError("숫자를 찾을 수 없음")
        except:
            # call_no 파싱 실패 시 아래 스마트 분류로 넘어감
            pass
        else:
            # 000-099: 총류
            if 0 <= code_num <= 99:
                return "총류"
            # 100-199: 철학
            elif 100 <= code_num <= 199:
                return "철학"
            # 200-299: 종교
            elif 200 <= code_num <= 299:
                return "종교"
            # 300-399: 사회과학
            elif 300 <= code_num <= 399:
                return "사회과학"
            # 400-499: 자연과학
            elif 400 <= code_num <= 499:
                return "자연과학"
            # 500-599: 기술과학
            elif 500 <= code_num <= 599:
                return "기술과학"
            # 600-699: 예술
            elif 600 <= code_num <= 699:
                return "예술"
            # 700-799: 언어
            elif 700 <= code_num <= 799:
                return "언어"
            # 800-899: 문학
            elif 800 <= code_num <= 899:
                # 문학은 더 세부적으로 나눌 수 있음
                if 810 <= code_num <= 819:
                    return "한국문학"
                elif 830 <= code_num <= 839:
                    return "영미문학"
                elif 850 <= code_num <= 859:
                    return "독일문학"
                elif 870 <= code_num <= 879:
                    return "프랑스문학"
                elif 880 <= code_num <= 889:
                    return "스페인문학"
                elif 890 <= code_num <= 899:
                    return "기타문학"
                return "문학"
            # 900-999: 역사
            elif 900 <= code_num <= 999:
                return "역사"
    
    # call_no가 없거나 파싱 실패 시 제목, 작가, 검색어로 스마트 분류
    all_text = f"{title} {author} {search_title}".lower()
    
    # 한국 문학 작가 목록 (주요 작가들)
    korean_authors = [
        "이상", "김유정", "채만식", "이태준", "이효석", "박태원", 
        "최명익", "현진건", "염상섭", "이광수", "김동인", "김동리",
        "김소월", "한용운", "윤동주", "이육사", "정지용", "서정주",
        "박목월", "조지훈", "백석", "이상화", "한용운",
        "박경리", "김동리", "황순원", "염상섭", "채만식", "이태준",
        "박완서", "이문열", "조정래", "황석영", "공지영", "은희경"
    ]
    
    # 영미 문학 작가 목록 (주요 작가들)
    english_authors = [
        "jane austen", "제인 오스틴", "오스틴", "shakespeare", "셰익스피어",
        "charles dickens", "찰스 디킨스", "디킨스", "virginia woolf", "버지니아 울프",
        "ernest hemingway", "헤밍웨이", "hemingway", "mark twain", "마크 트웨인",
        "f. scott fitzgerald", "피츠제럴드", "fitzgerald", "george orwell", "조지 오웰",
        "j.k. rowling", "롤링", "rowling", "tolki", "톨킨", "harry potter", "해리포터"
    ]
    
    # 영미 작가 이름이 포함되어 있으면 영미문학
    for english_author in english_authors:
        if english_author.lower() in all_text:
            return "영미문학"
    
    # 제목이나 작가에 한국 작가 이름이 포함되어 있으면 한국문학
    for korean_author in korean_authors:
        if korean_author.lower() in all_text:
            return "한국문학"
    
    # 유명 작품 제목으로 분류
    famous_works = {
        "pride and prejudice": "영미문학",
        "오만과 편견": "영미문학",
        "오만과": "영미문학",  # 오만과 편견 관련
        "제인 에어": "영미문학",
        "jane eyre": "영미문학",
        "해리포터": "영미문학",
        "harry potter": "영미문학"
    }
    
    for work, category in famous_works.items():
        if work.lower() in all_text:
            return category
    
    # 소설 관련 키워드
    novel_keywords = ["소설", "novel", "fiction", "날개", "삼대", "토지", "무정"]
    if any(keyword in all_text for keyword in novel_keywords):
        # 한국 관련 키워드가 있으면 한국문학
        if any(kw in all_text for kw in ["한국", "korea", "korean", "이상", "작가"]):
            return "한국문학"
        # 영미 작가나 영어 제목이 있으면 영미문학
        if any(auth.lower() in all_text for auth in english_authors):
            return "영미문학"
        return "문학"
    
    # 시 관련 키워드
    poetry_keywords = ["시집", "시선", "poetry", "poem", "시"]
    if any(keyword in all_text for keyword in poetry_keywords):
        if any(kw in all_text for kw in ["한국", "korea", "korean"]):
            return "한국문학"
        if any(auth.lower() in all_text for auth in english_authors):
            return "영미문학"
        return "문학"
    
    # 영어 제목이나 작가가 있으면 영미문학 가능성
    english_pattern = re.compile(r'[a-zA-Z]{3,}')
    if english_pattern.search(all_text):
        # 하지만 한국 작가나 한국 관련 키워드가 더 우선
        if not any(kw in all_text for kw in ["한국", "korea", "korean"] + [a.lower() for a in korean_authors]):
            # 영미 작가가 명시되어 있으면 영미문학
            if any(auth.lower() in all_text for auth in english_authors):
                return "영미문학"
            # 영어 제목이 있고 한국어가 거의 없으면 영미문학
            korean_pattern = re.compile(r'[가-힣]+')
            if not korean_pattern.search(all_text) or len([c for c in all_text if ord(c) >= 0xAC00 and ord(c) <= 0xD7A3]) < 3:
                return "영미문학"
    
    # 기본값: 기타
    return "기타"

# 책 정보를 추출하는 헬퍼 함수
def extract_book_info(item, search_title=""):
    """
    XML item에서 책 정보를 추출하는 함수
    """
    # 책 정보 추출하기
    book_title = item.find('title_info')
    title_text = book_title.text if book_title is not None and book_title.text else search_title
    
    # 출판사 정보
    publisher_info = item.find('publisher')
    publisher = publisher_info.text if publisher_info is not None and publisher_info.text else "출판사 정보 없음"
    
    # 작가 정보 추출 (여러 필드에서 시도)
    author_info = item.find('author_info') or item.find('author') or item.find('author_name')
    author = author_info.text if author_info is not None and author_info.text else ""
    
    # 검색어에서 작가 정보 추출 시도 (예: "날개 (작가:이상)" -> "이상")
    if not author and search_title:
        # 괄호 안의 "작가:" 패턴 찾기
        author_match = re.search(r'작가[:\s]*([^)]+)', search_title)
        if author_match:
            author = author_match.group(1).strip()
    
    # 분류 코드 (call_no)
    call_no_info = item.find('call_no')
    call_no = call_no_info.text if call_no_info is not None and call_no_info.text else ""
    
    # 책 표지 이미지
    image_info = item.find('image_url')
    image_url = image_info.text if image_info is not None and image_info.text else None
    
    # 카테고리 결정 (제목, 작가, 검색어 모두 전달)
    category = get_category_name(call_no, title=title_text, author=author, search_title=search_title)
    
    return {
        "title": title_text,
        "publisher": publisher,
        "author": author,
        "call_no": call_no,
        "category": category,
        "image_url": image_url,
        "search_title": search_title
    }

# 국립도서관 API에서 여러 책 정보를 가져오는 함수
def search_books(title, max_results=10):
    """
    책 제목을 입력하면 도서관 API에서 여러 개의 검색 결과를 찾아오는 함수
    네트워크가 느릴 때를 대비해서 여러 번 시도합니다
    """
    # 최대 3번까지 시도하기
    max_retries = 3
    retry_delay = 5  # 재시도 전 대기 시간 (초) - 서버 부하를 줄이기 위해 5초로 증가
    
    for attempt in range(max_retries):
        try:
            # API에 요청 보내기
            params = {
                "key": API_KEY,
                "kwd": title,
                "apiType": "xml",
                "pageSize": max_results  # 여러 결과 가져오기
            }
            
            # 브라우저처럼 보이게 헤더 추가하기 (서버가 봇으로 인식하지 않도록)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/xml, text/xml, */*',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Referer': 'https://www.nl.go.kr/'
            }
            
            # timeout을 30초로 늘려서 느린 네트워크도 기다릴 수 있게 함
            response = requests.get(API_BASE_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # XML 데이터를 읽어오기
            root = ET.fromstring(response.content)
            
            # 책 정보가 있는지 확인
            items = root.findall('.//item')
            
            if not items:
                return []
            
            # 여러 검색 결과 추출
            books = []
            for item in items[:max_results]:
                book_info = extract_book_info(item, search_title=title)
                books.append(book_info)
            
            return books
        
        except requests.exceptions.Timeout:
            # 시간 초과 오류가 발생했을 때
            if attempt < max_retries - 1:
                # 아직 재시도할 기회가 있으면 잠시 기다렸다가 다시 시도
                time.sleep(retry_delay)
                continue
            else:
                # 마지막 시도에서도 실패하면 오류 메시지 표시
                st.error(f"⏱️ 서버 응답이 너무 느립니다. 네트워크 연결을 확인해주세요. (시도 횟수: {max_retries}회)")
                return []
        
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
            # 연결이 끊기거나 네트워크 관련 오류가 발생했을 때
            error_msg = str(e)
            # ConnectionResetError인 경우 특별한 메시지 표시
            if "10054" in error_msg or "Connection aborted" in error_msg or "ConnectionResetError" in error_msg:
                if attempt < max_retries - 1:
                    # 재시도 전에 더 길게 대기 (서버 부하 때문일 수 있음)
                    time.sleep(retry_delay + 2)
                    continue
                else:
                    st.error(f"🔌 서버 연결이 끊어졌습니다. 잠시 후 다시 시도해주세요. (시도 횟수: {max_retries}회)")
                    return []
            else:
                # 다른 네트워크 오류
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    st.error(f"🌐 네트워크 오류가 발생했습니다: {error_msg} (시도 횟수: {max_retries}회)")
                    return []
        
        except Exception as e:
            # 기타 오류가 발생했을 때
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                st.error(f"❌ 책을 찾는 중 오류가 발생했습니다: {str(e)} (시도 횟수: {max_retries}회)")
                return []
    
    # 모든 시도가 실패한 경우
    return []

# 유사한 제목을 찾는 함수 (오타 교정용)
def find_similar_titles(search_query, max_suggestions=5):
    """
    검색 결과가 없을 때 유사한 제목을 찾아서 제안하는 함수
    검색어를 변형해서 다시 검색해보고, 유사한 제목들을 반환
    """
    suggestions = []
    
    # 검색어를 단어로 분리
    words = search_query.split()
    
    # 단어가 2개 이상이면 각 단어로 개별 검색
    if len(words) >= 2:
        for word in words:
            if len(word) >= 2:  # 너무 짧은 단어는 제외
                try:
                    # 각 단어로 검색 (최대 20개 결과)
                    results = search_books(word, max_results=20)
                    for book in results:
                        title = book.get('title', '')
                        if title and title not in suggestions:
                            suggestions.append(title)
                            if len(suggestions) >= max_suggestions * 2:  # 더 많이 가져와서 필터링
                                break
                except:
                    continue
    
    # 검색어의 일부를 사용해서 더 넓게 검색 (마지막 글자 제거)
    if len(search_query) > 2:
        partial_query = search_query[:-1]
        try:
            results = search_books(partial_query, max_results=20)
            for book in results:
                title = book.get('title', '')
                if title and title not in suggestions:
                    suggestions.append(title)
                    if len(suggestions) >= max_suggestions * 2:
                        break
        except:
            pass
    
    # 유사도 계산해서 가장 유사한 제목들만 반환
    if suggestions:
        # difflib을 사용해서 유사도가 높은 제목들만 선택
        close_matches = get_close_matches(
            search_query, 
            suggestions, 
            n=max_suggestions, 
            cutoff=0.3  # 최소 30% 유사도
        )
        return close_matches
    
    return []

# 세션 상태 초기화 - 앱이 처음 시작될 때 실행
if 'books' not in st.session_state:
    st.session_state.books = []  # 저장된 책 목록

if 'selected_view' not in st.session_state:
    st.session_state.selected_view = "모두 보기"  # 현재 보기 모드

if 'search_results' not in st.session_state:
    st.session_state.search_results = []  # 검색 결과 목록

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""  # 검색어

if 'search_type' not in st.session_state:
    st.session_state.search_type = "제목"  # 검색 타입 (제목/작가)

if 'display_count' not in st.session_state:
    st.session_state.display_count = 10  # 표시할 검색 결과 개수

if 'suggested_titles' not in st.session_state:
    st.session_state.suggested_titles = []  # 오타 교정 제안 제목 목록

# 메인 타이틀
st.title("📚 도서 기록장")
st.markdown("---")

# 사이드바 - 책 추가하기
with st.sidebar:
    st.header("📖 새 책 추가하기")
    
    # 검색 타입 선택
    search_type = st.radio(
        "검색 타입",
        ["제목", "작가"],
        index=0 if st.session_state.search_type == "제목" else 1,
        horizontal=True
    )
    st.session_state.search_type = search_type
    
    # 검색 폼 (엔터 키로도 검색 가능)
    with st.form("search_form", clear_on_submit=False):
        # 검색어 입력
        search_placeholder = "예: 해리포터" if search_type == "제목" else "예: 제인 오스틴"
        book_input = st.text_input(
            f"책 {search_type}을 입력하세요",
            placeholder=search_placeholder,
            key="book_search_input"
        )
        
        # 검색 버튼 (엔터 키로도 제출 가능)
        submitted = st.form_submit_button("🔍 검색", type="primary", use_container_width=True)
        
        if submitted:
            if book_input.strip():
                st.session_state.search_query = book_input.strip()
                st.session_state.display_count = 10  # 검색 시 초기화
                with st.spinner("책을 찾는 중..."):
                    # 더 많은 결과를 가져오기 위해 max_results를 크게 설정 (최대 100개)
                    search_results = search_books(book_input.strip(), max_results=100)
                    st.session_state.search_results = search_results
                    if not search_results:
                        search_type_name = "제목" if search_type == "제목" else "작가"
                        st.error(f"❌ {search_type_name} '{book_input.strip()}'으로 책을 찾을 수 없습니다. 검색어를 다시 확인해주세요.")
                        
                        # 오타 교정: 유사한 제목 찾기
                        if search_type == "제목":  # 제목 검색일 때만 오타 교정
                            with st.spinner("유사한 제목을 찾는 중..."):
                                similar_titles = find_similar_titles(book_input.strip(), max_suggestions=5)
                                st.session_state.suggested_titles = similar_titles
                                if similar_titles:
                                    st.info("💡 **이걸 찾으시나요?** 아래 제목을 클릭해보세요.")
                                else:
                                    st.session_state.suggested_titles = []
                        else:
                            st.session_state.suggested_titles = []
                    else:
                        st.session_state.suggested_titles = []  # 검색 성공 시 제안 목록 초기화
                        st.success(f"✅ {len(search_results)}개의 검색 결과를 찾았습니다!")
            else:
                st.warning(f"⚠️ 책 {search_type}을 입력해주세요.")
    
    st.markdown("---")
    
    # 보기 모드 선택
    st.header("📑 보기 모드")
    view_mode = st.radio(
        "보기 방식 선택",
        ["모두 보기", "카테고리별 보기"],
        index=0 if st.session_state.selected_view == "모두 보기" else 1
    )
    st.session_state.selected_view = view_mode
    
    st.markdown("---")
    
    # 통계 정보
    st.header("📊 통계")
    total_books = len(st.session_state.books)
    st.metric("총 책 수", total_books)
    
    # 카테고리별 책 수
    if total_books > 0:
        category_count = defaultdict(int)
        for book in st.session_state.books:
            category_count[book.get("category", "기타")] += 1
        
        st.subheader("카테고리별")
        for cat, count in sorted(category_count.items()):
            st.write(f"- {cat}: {count}권")

# 메인 콘텐츠 영역
# 제안된 제목이 있으면 표시 (오타 교정)
if st.session_state.suggested_titles and not st.session_state.search_results:
    st.header("💡 이걸 찾으시나요?")
    st.info("검색 결과가 없습니다. 아래 유사한 제목을 클릭해보세요.")
    st.markdown("---")
    
    for idx, suggested_title in enumerate(st.session_state.suggested_titles):
        if st.button(f"📖 {suggested_title}", key=f"suggest_main_{idx}", use_container_width=True):
            # 제안된 제목으로 다시 검색
            st.session_state.search_query = suggested_title
            st.session_state.display_count = 10
            st.session_state.suggested_titles = []  # 제안 목록 초기화
            with st.spinner("책을 찾는 중..."):
                new_search_results = search_books(suggested_title, max_results=100)
                st.session_state.search_results = new_search_results
                if new_search_results:
                    st.success(f"✅ {len(new_search_results)}개의 검색 결과를 찾았습니다!")
                    st.rerun()
    st.markdown("---")
    st.markdown("")

# 검색 결과가 있으면 표시
if st.session_state.search_results:
    st.header("🔍 검색 결과")
    total_results = len(st.session_state.search_results)
    displayed_results = min(st.session_state.display_count, total_results)
    search_type_name = st.session_state.search_type
    st.caption(f"'{st.session_state.search_query}' ({search_type_name}) 검색 결과: {displayed_results}개 표시 / 전체 {total_results}개")
    st.markdown("---")
    
    # 검색 결과를 카드 형태로 표시 (display_count만큼만)
    existing_titles = [b.get("title", "") for b in st.session_state.books]
    
    for idx, book in enumerate(st.session_state.search_results[:st.session_state.display_count]):
        is_existing = book["title"] in existing_titles
        
        # 컨테이너로 구분
        with st.container():
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                st.markdown(f"**📖 {book['title']}**")
                if book.get('author'):
                    # 작가 검색일 때 작가 이름 강조
                    author_text = book['author']
                    if st.session_state.search_type == "작가" and st.session_state.search_query.lower() in author_text.lower():
                        st.markdown(f"✍️ **작가:** **{author_text}** ⭐")
                    else:
                        st.caption(f"✍️ 작가: {author_text}")
                else:
                    st.caption("✍️ 작가: 정보 없음")
                st.caption(f"🏢 출판사: {book.get('publisher', '정보 없음')}")
            
            with col2:
                category = book.get('category', '기타')
                # 분야에 따라 이모지 다르게 표시
                category_icons = {
                    "한국문학": "🔵",
                    "영미문학": "🟢",
                    "문학": "🟣",
                    "사회과학": "🟠",
                    "기타": "⚪"
                }
                category_icon = category_icons.get(category, "📂")
                st.markdown(f"**{category_icon} 분야:** {category}")
                if book.get('call_no'):
                    st.caption(f"분류: {book.get('call_no')}")
            
            with col3:
                if is_existing:
                    st.warning("⚠️ 이미 추가됨")
                else:
                    if st.button("✅ 추가", key=f"add_book_{idx}", type="primary", use_container_width=True):
                        # 책 정보 복사본 생성
                        book_copy = book.copy()
                        book_copy["memo"] = ""
                        # 책 목록에 추가
                        st.session_state.books.append(book_copy)
                        # 검색 결과는 유지 (여러 책을 연속으로 추가할 수 있도록)
                        st.success(f"✅ '{book_copy['title']}' 추가되었습니다!")
                        st.rerun()
        
        st.markdown("---")
    
    # 더 보기 버튼 (더 많은 결과가 있을 때만 표시)
    if total_results > st.session_state.display_count:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📖 더 보기", key="load_more", type="secondary", use_container_width=True):
                # 10개씩 더 표시
                st.session_state.display_count += 10
                st.rerun()
        st.caption(f"현재 {displayed_results}개 표시 중 (전체 {total_results}개)")
    
    # 검색 결과 초기화 버튼
    if st.button("🔄 검색 초기화", key="clear_search"):
        st.session_state.search_results = []
        st.session_state.search_query = ""
        st.session_state.display_count = 10
        st.rerun()
    
    st.markdown("---")
    st.markdown("")

# 저장된 책 목록 표시
if len(st.session_state.books) == 0 and not st.session_state.search_results:
    # 책이 없을 때 안내 메시지
    st.info("👈 왼쪽 사이드바에서 책을 검색해보세요!")
elif len(st.session_state.books) > 0:
    if st.session_state.selected_view == "모두 보기":
        # 모두 보기 모드 - 모든 책을 한눈에 보기
        st.header("📚 모든 책 보기")
        
        # 카테고리별로 그룹화
        books_by_category = defaultdict(list)
        for book in st.session_state.books:
            category = book.get("category", "기타")
            books_by_category[category].append(book)
        
        # 카테고리별로 칼럼 레이아웃으로 표시
        for category, books in sorted(books_by_category.items()):
            st.subheader(f"📂 {category} ({len(books)}권)")
            
            # 한 줄에 여러 책을 표시하기 위해 컬럼 사용
            cols = st.columns(min(4, len(books)))  # 최대 4개 칼럼
            
            for idx, book in enumerate(books):
                col_idx = idx % 4
                
                with cols[col_idx]:
                    with st.container():
                        # 책 표지 이미지
                        if book.get("image_url"):
                            try:
                                st.image(book["image_url"], width=150, use_container_width=True)
                            except:
                                st.image("https://via.placeholder.com/150x200?text=No+Image", width=150)
                        else:
                            st.image("https://via.placeholder.com/150x200?text=No+Image", width=150)
                        
                        # 책 제목, 작가, 출판사
                        st.markdown(f"**{book['title']}**")
                        if book.get('author'):
                            st.caption(f"작가: {book.get('author')}")
                        st.caption(f"출판사: {book.get('publisher', '정보 없음')}")
                        
                        # 메모 영역
                        memo_key = f"memo_{book['title']}_{idx}"
                        memo = st.text_area(
                            "메모",
                            value=book.get("memo", ""),
                            key=memo_key,
                            height=100,
                            label_visibility="collapsed",
                            placeholder="이 책에 대한 메모를 작성하세요..."
                        )
                        
                        # 메모 저장
                        book["memo"] = memo
                        
                        # 삭제 버튼
                        if st.button("🗑️ 삭제", key=f"delete_{book['title']}_{idx}"):
                            st.session_state.books.remove(book)
                            st.rerun()
                        
                        st.markdown("---")
    
    else:
        # 카테고리별 보기 모드
        st.header("📑 카테고리별 보기")
        
        # 카테고리별로 그룹화
        books_by_category = defaultdict(list)
        for book in st.session_state.books:
            category = book.get("category", "기타")
            books_by_category[category].append(book)
        
        # 카테고리 탭으로 표시
        categories = sorted(books_by_category.keys())
        tabs = st.tabs(categories)
        
        for tab_idx, category in enumerate(categories):
            with tabs[tab_idx]:
                books = books_by_category[category]
                st.subheader(f"📂 {category} ({len(books)}권)")
                
                # 각 책을 카드 형태로 표시
                for idx, book in enumerate(books):
                    with st.expander(f"📖 {book['title']}", expanded=False):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # 책 표지 이미지
                            if book.get("image_url"):
                                try:
                                    st.image(book["image_url"], width=200, use_container_width=True)
                                except:
                                    st.image("https://via.placeholder.com/200x300?text=No+Image", width=200)
                            else:
                                st.image("https://via.placeholder.com/200x300?text=No+Image", width=200)
                        
                        with col2:
                            st.markdown(f"**제목:** {book['title']}")
                            if book.get('author'):
                                st.markdown(f"**작가:** {book.get('author')}")
                            st.markdown(f"**출판사:** {book.get('publisher', '정보 없음')}")
                            st.markdown(f"**분류 코드:** {book.get('call_no', '정보 없음')}")
                            
                            # 메모 영역
                            memo_key = f"memo_cat_{book['title']}_{idx}"
                            memo = st.text_area(
                                "메모",
                                value=book.get("memo", ""),
                                key=memo_key,
                                height=150,
                                placeholder="이 책에 대한 메모를 작성하세요..."
                            )
                            
                            # 메모 저장
                            book["memo"] = memo
                            
                            # 삭제 버튼
                            if st.button("🗑️ 삭제", key=f"delete_cat_{book['title']}_{idx}"):
                                st.session_state.books.remove(book)
                                st.rerun()

# 하단 안내
st.markdown("---")
st.caption("💡 팁: 책 제목을 입력하면 자동으로 분야별로 분류됩니다. 각 책에 메모를 작성하여 독서 기록을 남겨보세요!")

