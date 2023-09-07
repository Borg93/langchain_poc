import pandas as pd
from langchain.document_loaders.dataframe import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from custom_vectorstore import CombineRetrieverSet
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain import PromptTemplate


def read_df_from_json(filename, dtypes):
    return pd.read_json(filename, orient='records', lines=True, dtype=dtypes)

def add_metadata(sections, metadata_key, metadata_value_prefix):
    for i, section in enumerate(sections):
        section.metadata[metadata_key] = f"{metadata_value_prefix}{i}"

def create_chroma_db(sections_text_splitted, blue_boxes_sections_text_splitted, embeddings ,chroma_section,chroma_bbox ):
    Chroma.from_documents(sections_text_splitted, embeddings, persist_directory=chroma_section)
    Chroma.from_documents(blue_boxes_sections_text_splitted, embeddings, persist_directory=chroma_bbox)

def load_chroma_db(embeddings, chroma_section, chroma_bbox):
    chroma_sections_db = Chroma(embedding_function=embeddings, persist_directory=chroma_section)
    chroma_blue_boxes_db = Chroma(embedding_function=embeddings, persist_directory=chroma_bbox)
    return chroma_sections_db, chroma_blue_boxes_db


if __name__ == "__main__":

    openai_api_key = os.getenv("OPENAI_API_KEY") 

    dtype_dict = {'pagebluebox': 'str', 'joined_text': 'str'}
    df_sections_from_json = read_df_from_json('invandring_section_v9.json', dtype_dict)
    df_bluebox_from_json = read_df_from_json('invandring_blue_boxes_v9.json', dtype_dict)


    data_loader_sections = DataFrameLoader(data_frame=df_sections_from_json, page_content_column='text')
    data_loader_bb = DataFrameLoader(data_frame=df_bluebox_from_json, page_content_column='text')

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150, separators=["\n\n", "\n", " ", ""])

    sections_text_splitted = data_loader_sections.load_and_split(text_splitter=text_splitter)
    blue_boxes_sections_text_splitted = data_loader_bb.load_and_split(text_splitter=text_splitter)

    add_metadata(sections_text_splitted, "chunk_id_section", "")
    add_metadata(blue_boxes_sections_text_splitted, "chunk_id_archive", "")

    chroma_section= "chroma_sections_7"
    chroma_bbox = "chroma_blue_boxes_7"

    embeddings = OpenAIEmbeddings()

    create_chroma_db(sections_text_splitted, blue_boxes_sections_text_splitted, embeddings ,chroma_section,chroma_bbox )

    chroma_sections_db, chroma_blue_boxes_db = load_chroma_db(embeddings, chroma_section, chroma_bbox)

    k = 10
    vectorstore_sections_retriever = chroma_sections_db.as_retriever(search_kwargs={"k": k})
    vectorstore_blue_boxes_retriever = chroma_blue_boxes_db.as_retriever(search_kwargs={"k": k})

    vectorstore_combined_set_retriver_swapped = CombineRetrieverSet(
        chroma_sections_db=chroma_sections_db,
        chroma_blue_boxes_db=chroma_blue_boxes_db,
        section_retriever=vectorstore_sections_retriever,
        blue_boxes_retriever=vectorstore_blue_boxes_retriever
    )


    # llm = OpenAI(temperature=0)
    # compressor = LLMChainExtractor.from_llm(llm)
    # compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=vectorstore_combined_set_retriver)

    # compressed_docs = compression_retriever.get_relevant_documents("baltiska flyktningar")


    query_input ="""
    Estlandsvenskar
    """


    template = """You are an AI assistant for answering questions about the most recent state of the union address.
    You are given the following extracted parts of a long document and a question. Provide a conversational answer.
    If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
    If the question is not about the most recent state of the union, politely inform them that you are tuned to only answer questions about the most recent state of the union.
    Lastly, answer the question as if you were a pirate from the south seas and are just coming back from a pirate expedition where you found a treasure chest full of gold doubloons.
    Question: {question}
    =========
    {context}
    =========
    Answer should always be in Swedish text and structure in Markdown:"""

    QA_PROMPT = PromptTemplate(template=template, input_variables=[
                            "question", "context"])

    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    # llm=OpenAI(model_name="gpt-4",temperature=0)

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore_combined_set_retriver_swapped)
    query = """
    Jag har en släkting som flydde över till Sverige i slutet av andra världskriget (d v s 1944 eller början av 1945) och ska ha kommit via de vita bussarna* (eller på annat sätt). Finns det någon information kring hen, var kommer hen ifrån? Var placerades personen i Sverige? Finns det även bilder?
    """
    qa.run(query)