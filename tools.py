
import os
import requests
import json    

from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain.tools import BaseTool
from langchain_core.retrievers import Document
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import glob
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.document_loaders.directory import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter

import sqlite3




# Tạo hàm gọi API lấy dữ liệu tỷ giá vàng
def fetch_gold_data(api_url):
    gold_context = {}
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("DataList", {}).get("Data", [])[:7]
    except Exception as e:
        return {"error": f"Lỗi khi gọi API: {e}"}
        
    for n, item in enumerate(items, start=1):
        # Lấy giá trị các trường
        name = item.get(f"@n_{n}")
        gold_kara = item.get(f"@k_{n}")
        gold_content = item.get(f"@h_{n}")
        buy_price = item.get(f"@pb_{n}")
        sell_price = item.get(f"@ps_{n}")
        world_price = item.get(f"@pt_{n}")
        date_time = item.get(f"@d_{n}")

        gold_context[name] = (
            f"#TỶ GIÁ VÀNG {name} HÔM NAY:\n"
            f"##Tên vàng: {name}\n"
            f"##Hàm lượng kara: {gold_kara}\n"
            f"##Hàm lượng vàng: {gold_content}\n"
            f"##Giá mua vào: {buy_price}\n"
            f"##Giá bán ra: {sell_price}\n"
            f"##Giá thế giới: {world_price}\n"
            f"##Thời gian cập nhật: {date_time}"
        )

    return gold_context

def create_vectorstore():

    embeddings = OpenAIEmbeddings()
    # Kiểm tra nếu database Chroma đã tồn tại, thì xóa collection để khởi động lại từ đầu

    db_name = "vector_db"

    if os.path.exists(db_name):
        Chroma(persist_directory=db_name, embedding_function=embeddings).delete_collection()
    
    # đọc tất cả tài liệu sử dụng LangChain loader
    folders = glob.glob("knowledge-base/*")
    text_loader_kwargs={'autodetect_encoding': True}

    if not folders:
        raise ValueError("Không có folders nào để đọc. Kiểm tra dữ liệu đầu vào!")

    documents = []

    for folder in folders:
        doc_type = os.path.basename(folder)
        loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
        folder_docs = loader.load()
        for doc in folder_docs:
            doc.metadata["doc_type"] = doc_type
            documents.append(doc)

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on = [
        ("#", "main_section"),
        ("##", "sub_section"),
        ("###", "detail")
    ]
    )

    all_chunks = []

    for doc in documents:
        # Tách nội dung của từng file Markdown theo header
        chunks = markdown_splitter.split_text(doc.page_content)
    
        # Giữ nguyên metadata gốc
        for chunk in chunks:
            chunk.metadata.update(doc.metadata)

            # Ghép các tiêu đề header vào nội dung văn bản
            headers = " | ".join([
                chunk.metadata.get("main_section", ""),
                chunk.metadata.get("sub_section", ""),
                chunk.metadata.get("detail", "")
            ])
            headers = headers.strip(" |")  # Xóa dấu '|' thừa

            # Cập nhật lại nội dung chunk
            if headers:
                chunk.page_content = f"{headers}\n{chunk.page_content}".strip()

            all_chunks.append(chunk)

    if not all_chunks:
        raise ValueError("Không có chunk nào để tạo vectorstore. Kiểm tra dữ liệu đầu vào!")

    # Tạo vector store bằng Chroma
    vectorstore = Chroma.from_documents(
        documents=all_chunks,          # Danh sách các đoạn văn bản đã chia nhỏ
        embedding=embeddings,          # Hàm embedding
        persist_directory=db_name      # Thư mục lưu trữ database
    )
    return vectorstore

class RetriveInput(BaseModel):
  query: str = Field("", description="Chuỗi truy vấn tìm kiếm do người dùng nhập")

class RetrieveTool(BaseTool):
  name: str = 'retriever_tool'
  description: str = "Công cụ thu thập thông tin về các dịch vụ của ngân hàng VIB " \
  "gồm tài khoản, thẻ, tài khoản tiết kiệm, ứng dụng ngân hàng điện tử, khoản vay"
  args_schema: Type[BaseModel] = RetriveInput
  return_direct: bool = False

  _vector_store: Type[Chroma]
  _k: int

  def __init__(self, vectorstores, **kwargs) -> None:
    super().__init__(**kwargs)
    self._vector_store = vectorstores
    self._k = kwargs.get("k", 10)

  def _run(
      self,
      query: str,
      run_manager: Optional[CallbackManagerForToolRun] = None
  ) -> str:
    results = self._vector_store.similarity_search(query, k=self._k)
    documents = [doc.page_content for doc in results]

    return "\n\n".join(documents)
  


class GoldPriceRetrieveTool(BaseTool):
    name: str = 'gold_price_retriever'
    description: str =  "Công cụ thu thập thông tin về tỷ giá vàng."
    args_schema: Type[BaseModel] = RetriveInput
    return_direct: bool = False
    _k: int
    _api_url: str = "http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v" 
    def __init__(self, api_url: str = None, **kwargs):
        super().__init__(**kwargs)
        if api_url:
            self._api_url = api_url
        self._k = kwargs.get("k", 7)
    def _run(
        self,
        **kwargs
    ) -> str:
        #Gọi hàm gọi API lấy dữ liệu tỷ giá vàng
        gold_docs = fetch_gold_data(self._api_url)
        gold_documents = [
            Document(page_content=v, metadata={"doc_type": "gold"})
            for v in gold_docs.values()
        ]
        documents = [doc.page_content for doc in gold_documents]
        return "\n\n".join(documents)
    

def save_message(role, content, db_file="chatbot_history.db"):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (role, content) VALUES (?, ?)",
        (role, content)
    )
    conn.commit()



