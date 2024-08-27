import os
import openai
import sys
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_upstage import ChatUpstage
from langchain_upstage import UpstageEmbeddings # Embeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()
api_key = os.environ.get("SOLAR_API_KEY")

persist_directory = 'docs/chroma/'

filter_embedding = OllamaEmbeddings(model="EEVE-Korean-10.8B-FOR-FILTER:latest", base_url="http://172.17.0.8:11434")
filter_llm = ChatOllama(model="EEVE-Korean-10.8B-FOR-FILTER:latest", base_url="http://172.17.0.8:11434", temperature=0)

solar_embedding = UpstageEmbeddings(
    api_key=api_key,
    model="solar-embedding-1-large"
)

solar_llm = ChatUpstage(api_key=api_key, temperature=0)

chat_llm = ChatUpstage(api_key=api_key, temperature=0)

def update_vector_db(candidate_num, file_name, filter_embedding=filter_embedding, filter_llm=filter_llm,
                     solar_embedding=solar_embedding, solar_llm=solar_llm):
    # Load data
    loader = PyPDFLoader(file_name)
    docs = loader.load()
    
    # setup splitter --> here we will use recursiveCharacterSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""],
    )

    # get split result
    splits = text_splitter.split_documents(docs)
    # ---------------------------------------------------------
    # First Chain(FILTERING)
    # ---------------------------------------------------------
    
    map_prompt = """
    You are a helpful AI Filtering engine.
    You will be given a single passage of a document resume or curriculum vitae in Korean or English. 
    This section will be enclosed in triple backticks (```)
    AI Filtering engine task is to identify and remove any personal identifiable information (PII) such as phone numbers, emails, web addresses, and physical addresses.
    Specifically, if you find a name, replace it with "Candidate No.{candidate_num}". 
    While removing PII, ensure that all job-related information such as education, work experience, skills, and awards are accurately preserved and summarized. 
    Do not omit any important details related to the candidate's qualifications and experience but you should remove the PII except replaced name.
    Do not contain any other information that I didn't ask.

    ```{text}```
    FULL SUMMARY:
    """
    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text", "candidate_num"])
    
    map_chain = load_summarize_chain(llm=filter_llm,
                             chain_type="stuff",
                             prompt=map_prompt_template)
    
    
    # Make an empty list to hold your summaries
    summary_list = []

    # Loop through a range of the lenght of your splits
    for i, doc in enumerate(splits):

        # Go get a summary of the chunk
        chunk_summary = map_chain.invoke({"input_documents": [doc], "text": doc.page_content, "candidate_num": candidate_num})

        # Append that summary to your list
        summary_text = chunk_summary['output_text']
        summary_list.append(summary_text)
        
        # print(f"Preview: {summary_text}"+"...","\n")
        # print("==================================================================")
    
    # ---------------------------------------------------------
    # Second Chain(SUMMARY)
    # ---------------------------------------------------------
    
    
    summaries = "\n".join(summary_list)
    
    # Convert it back to a document
    summaries = Document(page_content=summaries)
    
    combine_prompt = """
    You are a helpful AI SCOUT BOT! Your name is scouty.
    You will be given a series of summaries from a resume in Korean or English. 
    The summaries will be enclosed in triple backticks (```)
    AI SCOUT BOT goal is to give a verbose summary of less than 4000 characters in Korean only.
    Ensure that all important job-related information such as education, work experience, skills, and awards are included.
    Only answer it based on a given information.
    The reader should be able to grasp what happened in the document for hiring the candidate.
    Please begin the summary with the {candidate_num}!

    ```{text}```
    VERBOSE SUMMARY:
    """
    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["candidate_num", "text"])
    
    resume_chain = load_summarize_chain(llm=solar_llm,
                             chain_type="stuff",
                             prompt=combine_prompt_template,
                             verbose=False # Set this to true if you want to see the inner workings
                             )
    

    output = resume_chain.invoke({"input_documents": [summaries], "candidate_num": candidate_num, "text": summaries})
    final_output = output['output_text']
    # print(final_output)
   

    # ---------------------------------------------------------
    # Third Chain (final chain to vector DB)
    # ---------------------------------------------------------
    
    # setup splitter --> here we will use recursiveCharacterSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=100,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""],
    )

    # get split result
    splits_output = text_splitter.split_text(final_output)

    vectordb = Chroma.from_texts(
        texts=splits_output,
        embedding=solar_embedding,
        persist_directory=persist_directory
    )
    
    return vectordb

def get_mertics_llm(vectordb, job_position, job_name):
    metrics_prompt_template = """
            You are a helpful AI SCOUT BOT! Your name is scouty.
            If the context is not relevant or is difficult to provide a specific definition or detailed understanding, 
            please answer the question by using your own knowledge about the topic
            
            If question asking related with calculate or evaluate candidate resumes You should following below instructions.
            
            Here are the metrics to evaluate candidate resumes. 
            For all candidates, please calculate the following metrics, and all metric scores should be in the range of 1(bad) to 5(good). 
            Please provide the results in a JSON format, where the keys are the candidate names, and the values are another JSON object containing the scores for each metric.

            Metrics to evaluate:
            (1). experience: Measure the total years of relevant work experience.
            (2). relevance: Assess how closely the applicant's experience aligns with the job domain.
            (3). education: Evaluate the level and relevance of the applicant's education to the job requirement.
            (4). skills: Rate the proficiency in key technical skills required for the job.

            The output should be in the following format:
            {{
                "Candidate Name 1": {{
                    "experience": X,
                    "relevance": Y,
                    "education": Z,
                    "skills": W,
                }},
                ...
            }}
            
            {context}
            
            Question: {question}
            """
    Metrics_PROMPT = PromptTemplate(
                        template=metrics_prompt_template, 
                        input_variables=["context", "question"]
    )

    # we define memory for chat history
    metrics_memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # retrieval chain
    metrics_qa = ConversationalRetrievalChain.from_llm(
        chat_llm,
        retriever=vectordb.as_retriever(search_type="mmr",
                                        search_kwargs={'k': 10, 'fetch_k': 50}),
        chain_type="stuff", # if want to use other chain type, you may need other parameter setup for ConversationRetrievalChain 
        memory=metrics_memory,
        combine_docs_chain_kwargs={"prompt": Metrics_PROMPT}
    )

    # education = "msc"
    question = f"""
    I should rank all candidates based on their background to be {job_position} {job_name} with scale in range 1 to 5.
    """
    metrics_result = metrics_qa.invoke({"question": question})
    metrics_result = metrics_result['answer'].replace('\n\n',' ').replace('\n',' ')
    return metrics_result


def scouty_chat_llm(vectordb, metrix_txt, question):
    
    # preparing our custom prompt
    prompt_template = f"""
            You are a helpful AI SCOUT BOT! Your name is scouty. 
            please answer the question by using your own knowledge about the topic
            please only refer based on this metrics for ranking information of each cadidates : {metrix_txt.replace("}",'').replace("{","")}
            please provide a concise answer in 5 sentences or less.
            At the end of your answer, explicitly state that you need to review it further.
            
            {{context}}
            
            Question: {{question}}
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
        chat_llm,
        retriever=vectordb.as_retriever(search_type="mmr",
                                        search_kwargs={'k': 10, 'fetch_k': 50}),
        chain_type="stuff", # if want to use other chain type, you may need other parameter setup for ConversationRetrievalChain 
        memory=memory,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )

    result = qa.invoke({"question": question})
    result['answer'].replace('\n\n',' ').replace('\n',' ')
    print(result)
    return result