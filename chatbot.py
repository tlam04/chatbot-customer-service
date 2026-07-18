
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from tools import RetrieveTool, GoldPriceRetrieveTool, save_message


def create_chatbot(vectorstore):
    
    MODEL = "gpt-4o-mini"

    # tạo mô hình chat với OPEN AI
    llm = ChatOpenAI(temperature=0.7, model_name=MODEL, max_tokens=1000)

    system_message = (
    "Bạn là chuyên gia chăm sóc khách hàng thông minh tại ngân hàng VIB."
    "Nhiệm vụ của bạn là trả lời các câu hỏi liên quan đến tài khoản, thẻ, tài khoản tiết kiệm, ứng dụng ngân hàng điện tử, khoản vay và thông tin tỷ giá vàng một cách ngắn gọn và chính xác. "
    "Nếu bạn không biết câu trả lời, hãy trả lời: 'Để được hỗ trợ tốt hơn với câu hỏi này hãy liên hệ tổng đài qua số 1900 2200 (1.000 đ/phút) hoặc gửi email tại dvkh247@vib.com.vn.'."
    "Tuyệt đối không bịa ra thông tin nếu không có ngữ cảnh liên quan được cung cấp."
    )

    retriever_tool = RetrieveTool(vectorstores=vectorstore)
    gold_retriever_tool = GoldPriceRetrieveTool()

    agent = create_agent(
        model = llm,
        tools = [retriever_tool, gold_retriever_tool],
        system_prompt = system_message
    )

    def chat(question, history):
        if history is None:
            history = []

        messages = history.copy()

        messages.append({"role": "user", "content": question})

        result = agent.invoke({"messages": messages})

        bot_reply = result['messages'][-1].content

        save_message("user", question)
        save_message("assistant", bot_reply)

        #add to history
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": bot_reply})

        return "", history
    return chat