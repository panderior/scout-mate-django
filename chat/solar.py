import os
from dotenv import load_dotenv
from .models import UploadedFiles

from langchain_upstage import ChatUpstage
from langchain_upstage import UpstageEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

load_dotenv()
api_key = os.environ.get("SOLAR_API_KEY")

embeddings = UpstageEmbeddings(
    api_key=api_key,
    model="solar-embedding-1-large"
)

chat = ChatUpstage(api_key=api_key)

def ChatWithSolar(question):
    # =================== #
    #   Upload pdf path   #
    # =================== #
    # uploaded_files = UploadedFiles.objects.all()
    
    file_list = [
        '/workspace/BALAB_Hyeonji/Graduate/202408_LLM_Solar_Hackerthon/scout-mate-django/static/CV_정현지.pdf'
    ]
    
    # load data
    loaders = []
    for file_name in file_list:
        loaders.append(PyPDFLoader(file_name))

    docs = []
    for loader in loaders:
            docs.extend(loader.load())

    # setup splitter --> here we will use recursiveCharacterSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""],
    )

    # get split result
    splits = text_splitter.split_documents(docs)

    # ================ #
    #   vector store   #
    # ================ #
    persist_directory = 'docs/chroma/'

    vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embeddings, # fix : embedding -> embeddings
    persist_directory=persist_directory
    )

    # ============= #
    #   Retrieval   #
    # ============= #

    prompt_template = """If the context is not relevant or is difficult to provide a specific definition or detailed understanding, 
        please answer the question by using your own knowledge about the topic
        and Plase Using English
        
        {context}
        
        Question: {question}
        """
    PROMPT = PromptTemplate(
                        template=prompt_template, 
                        input_variables=["context", "question"]
    )

    # we define memory for chat history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # retrieval chain
    qa = ConversationalRetrievalChain.from_llm(
        chat, # fix : llm -> chat
        retriever=vectordb.as_retriever(),
        chain_type="stuff", # if want to use other chain type, you may need other parameter setup for ConversationRetrievalChain 
        memory=memory,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )

    result = qa.invoke({"question": question})
    result = result['answer'].replace('\n\n',' ').replace('\n',' ')

    return result