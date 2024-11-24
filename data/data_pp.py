from selenium import webdriver
from bs4 import BeautifulSoup
from langchain_community.document_loaders import Docx2txtLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re


def fetch_html_with_selenium(url):
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

def extract_content_wrap(html):
    soup = BeautifulSoup(html, "html.parser")
    content_wraps = soup.find_all("div", class_="content-wrap")
    extracted_texts = [content.get_text(separator="\n", strip=True) for content in content_wraps]
    return "\n".join(extracted_texts)

def clean_text(text):
    soup= BeautifulSoup(text,"html.parser")
    cleaned_text = soup.get_text(separator ="\n")

    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

urls = [
    "https://media.ajou.ac.kr/media/degree/major.do",
    " https://media.ajou.ac.kr/media/intro/greeting.do",
    "https://media.ajou.ac.kr/media/intro/intro.do",
    "https://media.ajou.ac.kr/media/intro/career.do",
    "https://media.ajou.ac.kr/media/intro/location.do",
    "https://media.ajou.ac.kr/media/degree/graduation.do",
    "https://media.ajou.ac.kr/media/degree/objective.do",
    "https://media.ajou.ac.kr/media/degree/subjects.do",
    "https://media.ajou.ac.kr/media/people/faculty.do",
    "https://media.ajou.ac.kr/media/people/staff.do"
]

all_texts = []
for url in urls:
    html_content = fetch_html_with_selenium(url)
    extracted_text = extract_content_wrap(html_content)
    all_texts.append(extracted_text)

from langchain_community.document_loaders import Docx2txtLoader
from langchain.schema import Document
documents = [
    Document(page_content=text, metadata={"source": url})
    for text, url in zip(all_texts, urls)
]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
split_texts = text_splitter.split_documents(documents)
cleaned_split_texts =[clean_text(text.page_content) for text in split_texts]

txt_docs = [
    Document(page_content=text, metadata={"source": f"CleanedText {i}"})
    for i, text in enumerate(cleaned_split_texts)
]


loader = Docx2txtLoader('./media.docx')
document_list=loader.load_and_split(text_splitter=text_splitter)

all_documents = txt_docs + document_list