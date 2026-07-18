# chatbot-customer-service
chatbot customer service for bank use VIB Bank public knowledge and RAG
Phần 1:	Tải mã nguồn
Tải mã nguồn và lưu ở thư mục bất kì tại (thay Admin bằng tên users đặt trên máy tính của bạn): C:\Users\Admin\...
Phần 2:	Cài đặt Anaconda
Tải Anaconda từ: https://www.anaconda.com/download. Cần tạo tài khoản để được tải miễn phí.
Chạy trình cài đặt và làm theo hướng dẫn. Lưu ý rằng Anaconda chiếm vài GB dung lượng và quá trình cài đặt có thể mất thời gian.
Phần 3:	Chạy mã nguồn
1.	Tạo môi trường ảo trong Anaconda
- Mở Anaconda Prompt:
Tìm kiếm Anaconda Prompt trong Start Menu và mở nó.
Điều hướng đến thư mục gốc của mã nguồn bằng lệnh sau (thay đường dẫn bằng đường dẫn thực tới nơi lưu file mã nguồn): cd C:\Users\Admin\Projects\vib_chatbot.
Chạy lệnh sau để tạo môi trường từ file environment.yml đã được cấu hình sẵn trong thư mục mã nguồn: conda env create -f environment.yml
Bước 2: Mở Anaconda Prompt
Bước 3: Điều hướng tới thư mục mã nguồn
Gõ cd + paste đường dẫn tới thư mục mã nguồn vừa copy và nhấn enter
Lúc này Anaconda Prompt sẽ trỏ tới thư mục mã nguồn
Bước 4: Tạo môi trường ảo
Gõ conda env create -f environment.yml và nhấn enter
2.	Kích hoạt môi trường
Sau khi cài đặt hoàn tất, kích hoạt môi trường mới bằng lệnh: conda activate llms
Nếu thành công, bạn sẽ thấy (llms) xuất hiện trong dòng lệnh, báo hiệu rằng môi trường đã được kích hoạt.
3.	Chạy mã nguồn
Sau khi kích hoạt môi trường ảo thành công, sử dụng lệnh sau để chạy file main.py để khởi động chatbot (thay đường dẫn bằng đường dẫn thực tế tới file main.py):
python C:\Users\Admin\Projects\vib_chatbot\agents\main.py
Sau khi nhập lệnh, sẽ có thông báo nếu chatbot khởi chạy thành công và địa chỉ IP để sử dụng chatbot.
Nhập close và nhấn enter để đóng chatbot.
