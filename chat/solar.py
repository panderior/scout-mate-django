from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, SystemMessage

chat = ChatUpstage(api_key="up_R7NKyxZ1MIMcogbWOvjsJij6108aS")

def ChatWithSolar(question):
    messages = [
        SystemMessage(
            content="You are a helpful assistant."
        ),
        HumanMessage(
            content=f"{question}"
        )
    ]

    response = chat.invoke(messages).content

    print(response)
    
    return response