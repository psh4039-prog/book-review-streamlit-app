import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

# ----------------------------
# 함수: 부크크에서 도서 이미지/URL 검색
# ----------------------------
def fetch_bookk_image_url(title):
    search_url = f"https://bookk.co.kr/search?keyword={urllib.parse.quote(title)}"
    response = requests.get(search_url)
    if response.status_code != 200:
        return None, None
    soup = BeautifulSoup(response.text, 'html.parser')
    link_tag = soup.select_one('.bookListType01 li a')
    img_tag = soup.select_one('.bookListType01 li img')
    if link_tag and img_tag:
        return "https://bookk.co.kr" + link_tag['href'], img_tag['src']
    return None, None

# ----------------------------
# Streamlit UI 시작
# ----------------------------
st.title("📚 단행본 검토 후보 도서 수집기 (수동입력용)")

if 'books' not in st.session_state:
    st.session_state.books = []

col1, col2 = st.columns([2, 1])
with col1:
    title = st.text_input("도서명")
    author = st.text_input("작가명")
    pub_date = st.text_input("출간일")
    isbn = st.text_input("ISBN")
    price = st.text_input("정가")
with col2:
    if st.button("조회 및 추가"):
        if title:
            url, img = fetch_bookk_image_url(title)
            new_book = {
                '도서명': title,
                '작가명': author,
                '출간일': pub_date,
                'ISBN': isbn,
                '정가': price,
                '이미지': img or '',
                'URL': url or '',
                '판매량(외부)': '',
                '비고': '',
                '분류': '검토 후보 도서',
                '진행': '검토중'
            }
            st.session_state.books.append(new_book)

# ----------------------------
# 도서 카드 출력
# ----------------------------
def update_field(index, field):
    st.session_state.books[index][field] = st.session_state[f"{field}_{index}"]

for i in range(0, len(st.session_state.books), 2):
    cols = st.columns(2)
    for j in range(2):
        idx = i + j
        if idx >= len(st.session_state.books):
            break
        book = st.session_state.books[idx]
        with cols[j]:
            st.image(book['이미지'], width=200)
            st.markdown(f"**제목:** {book['도서명']}")
            st.markdown(f"**작가:** {book['작가명']}")
            st.markdown(f"**출간일:** {book['출간일']}")
            st.markdown(f"**ISBN:** {book['ISBN']}")
            st.markdown(f"**정가:** {book['정가']}")
            st.text_input("판매량(외부)", key=f"판매량(외부)_{idx}", value=book['판매량(외부)'], on_change=update_field, args=(idx, '판매량(외부)'))
            st.text_input("비고", key=f"비고_{idx}", value=book['비고'], on_change=update_field, args=(idx, '비고'))
            st.selectbox("분류", ["검토 후보 도서", "참고 도서"], key=f"분류_{idx}", index=["검토 후보 도서", "참고 도서"].index(book['분류']), on_change=update_field, args=(idx, '분류'))
            st.selectbox("진행여부", ["확정", "검토중", "보류", "불가"], key=f"진행_{idx}", index=["확정", "검토중", "보류", "불가"].index(book['진행']), on_change=update_field, args=(idx, '진행'))
            if st.button("삭제", key=f"삭제_{idx}"):
                st.session_state.books.pop(idx)
                st.experimental_rerun()
            st.markdown(f"[관련 기사 보기](https://search.naver.com/search.naver?query={urllib.parse.quote(book['도서명'])})")

# ----------------------------
# 저장 기능
# ----------------------------
if st.button("저장하기"):
    df = pd.DataFrame(st.session_state.books)
    st.download_button("📥 엑셀 다운로드", data=df.to_csv(index=False), file_name="book_review_list.csv", mime="text/csv")
