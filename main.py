from interface import launch_ui
import sqlite3
import os
from dotenv import load_dotenv
from tools import create_vectorstore

def main():
    load_dotenv()
    db_file = 'chatbot_history.db'

    is_new_db = not os.path.exists(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    if is_new_db:
        cursor.execute("""
            CREATE TABLE chat_history (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Tạo database thành công")
    else: print("Đã kết nối với databse")
    
    print("Chat bot đang khởi động...")
    vectorstore = create_vectorstore()
    demo = launch_ui(vectorstore)

    running = demo.launch(prevent_thread_lock=True)
    if running:
        print("Chatbot đang chạy, truy cập IP trên để sử dụng chatbot")
        close_chat = input("Nhập 'close' để dừng chatbot: ")
    else: print("Khởi động chatbot thất bại, có lỗi xảy!")
    
    if close_chat == "close":
        demo.close()
        print("Đã dừng chatbot")

if __name__ == "__main__":
    main()


