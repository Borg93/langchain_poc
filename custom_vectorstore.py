from pydantic import BaseModel
from langchain.schema.retriever import BaseRetriever, Document
from typing import List
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings


class CombineRetrieverSet(BaseRetriever):
    chroma_sections_db: Chroma
    chroma_blue_boxes_db: Chroma
    section_retriever: BaseRetriever
    blue_boxes_retriever: BaseRetriever

    class Config:
        arbitrary_types_allowed = True

    def get_relevant_documents(self, query: str, k: int= 10) -> List[Document]:
        docs_sections = self._retrieve_and_add_metadata(
            self.section_retriever, query, k, self.chroma_blue_boxes_db, "archive"
        )
        docs_blue_boxes = self._retrieve_and_add_metadata(
            self.blue_boxes_retriever, query, k, self.chroma_sections_db, "section"
        )
        filtered_docs = self._filter_and_concat(docs_sections,docs_blue_boxes )
        swapped_filtered_docs=  self._swap_page_content(filtered_docs)

        return swapped_filtered_docs

    def _swap_page_content(self,docs):
        temp_swap_list = []
        for doc in docs:
            if doc.metadata.get("joined_text_archive"):
                  doc.metadata["current_page_content"] = doc.page_content
                  doc.page_content = f"Section_context: {doc.metadata['joined_text']} \n Archive_context: {doc.metadata['joined_text_archive']}"
            else:
                doc.metadata["current_page_content"] = doc.page_content
                doc.page_content = f"Section_context: {doc.metadata['joined_text_section']} \n Archive_context: {doc.metadata['joined_text']}"
            temp_swap_list.append(doc)
        return temp_swap_list

    def _retrieve_and_add_metadata(
        self,
        primary_retriever,
        query,
        k,
        secondary_db,
        db_to_join
    ):
        docs_from_primary = primary_retriever.get_relevant_documents(query=query, k=k)

        merged_docs = []
        for doc in docs_from_primary:
            meta_key = doc.metadata.get("pagebluebox")
            if meta_key and meta_key != "None":
                matching_docs_from_secondary = secondary_db.get(where={"pagebluebox": meta_key})

                docs_list = [doc_from_secondary for doc_from_secondary in matching_docs_from_secondary['documents']]
                pagenumbers_list = [meta["pagenumber"] for meta in matching_docs_from_secondary['metadatas']]
                chunk_id_list = [meta[f"chunk_id_{db_to_join}"] for meta in matching_docs_from_secondary['metadatas']]

                doc.metadata[f"text_chunk_{db_to_join}"] = docs_list
                doc.metadata[f"pagenumber_{db_to_join}"] = pagenumbers_list
                doc.metadata[f"chunk_id_{db_to_join}"] = chunk_id_list
                doc.metadata[f"joined_text_{db_to_join}"] = matching_docs_from_secondary['metadatas'][0]["joined_text"]

            merged_docs.append(doc)

        return merged_docs

    def _match_conditions(self, dict_a, dict_b):
        joined_text_a = dict_a.metadata.get('joined_text')
        joined_text_b = dict_b.metadata.get('joined_text')
        joined_text_section_b = dict_b.metadata.get('joined_text_section')
        joined_text_archive_a = dict_a.metadata.get('joined_text_archive')

        condition1 = (joined_text_a == joined_text_section_b and
                      joined_text_archive_a == joined_text_b)

        condition2 = (joined_text_b == joined_text_archive_a and
                      joined_text_section_b == joined_text_a)

        return condition1 or condition2

    def _filter_and_concat(self, list_a, list_b):
        seen = set()
        filtered_list = []

        for dict_a in list_a:
            for dict_b in list_b:
                if self._match_conditions(dict_a, dict_b):
                    if id(dict_b) not in seen:
                        seen.add(id(dict_b))
                        filtered_list.append(dict_b)

                    if id(dict_a) not in seen:
                        seen.add(id(dict_a))
                        filtered_list.append(dict_a)

        return filtered_list

if __name__ == "__main__":

    embeddings = OpenAIEmbeddings()

    # Initialize chroma_sections_db and chroma_blue_boxes_db
    chroma_section= "chroma_sections_7"
    chroma_bbox = "chroma_blue_boxes_7"
    chroma_sections_db = Chroma(embedding_function=embeddings, persist_directory=chroma_section)
    chroma_blue_boxes_db = Chroma(embedding_function=embeddings, persist_directory=chroma_bbox)


    k = 10
    vectorstore_sections_retriever = chroma_sections_db.as_retriever(search_kwargs={"k": k})
    vectorstore_blue_boxes_retriever = chroma_blue_boxes_db.as_retriever(search_kwargs={"k": k})

    vectorstore_combined_set_retriver_swapped = CombineRetrieverSet(
        chroma_sections_db=chroma_sections_db,
        chroma_blue_boxes_db=chroma_blue_boxes_db,
        section_retriever=vectorstore_sections_retriever,
        blue_boxes_retriever=vectorstore_blue_boxes_retriever
    )

    # Use it to retrieve relevant documents
    query_input = "Estlandssvenskar"
    filtered_docs = vectorstore_combined_set_retriver_swapped.get_relevant_documents(query=query_input, k=10)
