import weaviate
import os
import pandas as pd


# Initialize Weaviate client
def initialize_client():
    client = weaviate.Client(
        url="https://arkiv-guider-p3k6ohxb.weaviate.network",
        auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key),
        additional_headers={
            "X-Cohere-Api-Key": cohere_api_key,
        },
        timeout_config=(20, 240)
    )

    if not client.is_ready():
        raise Exception("Weaviate client is not ready!")
    else:
        print("Weaviate client is ready!")

    return client

# Delete existing schema
def delete_existing_schema(client):
    client.schema.delete_class("Documents")

# Create a new schema
def create_schema(client):
    article_schema = {
        "class": "Documents",
        "description": "Documents for Indvandring example",
        "vectorizer": "text2vec-cohere",
        "moduleConfig": {
            "text2vec-cohere": {
                "model": "multilingual-22-12",
                "truncate": "NONE"
            },
        },
        "vectorIndexConfig": {
            "distance": "dot"
        },

        "properties": [
        {
            "name": "h1",
            "dataType": [ "text" ],
            "description": "Title of chapter from TOC",
            "moduleConfig": { "text2vec-cohere": { "skip": True } }
        },
        {
            "name": "h2",
            "dataType": [ "text" ],
            "description": "Sub header",
            "moduleConfig": { "text2vec-cohere": { "skip": True } }
        },
        {
            "name": "paragraph",
            "dataType": [ "text" ],
            "description": "paragraph body",
            "moduleConfig": {
                "text2vec-cohere": {
                    "skip": False,
                    "vectorizePropertyName": False
                }
            }
        },
            {
            "name": "archive",
            "dataType": [ "text" ],
            "description": "archive body",
            "moduleConfig": {
                "text2vec-cohere": {
                    "skip": False,
                    "vectorizePropertyName": False
                }
            }
        },
        {
            "name": "page_text",
            "dataType": [ "string" ],
            "description": "Paragraph's page number",
            "moduleConfig": { "text2vec-cohere": { "skip": True } }
        },
        {
            "name": "page_archive",
            "dataType": [ "string" ],
            "description": "Archive's page number",
            "moduleConfig": { "text2vec-cohere": { "skip": True } }
        },
        {
            "name": "page_archive_split",
            "dataType": [ "string" ],
            "description": "Archive's page number, but splitted over multiple pages",
            "moduleConfig": { "text2vec-cohere": { "skip": True } }
        },
        ]
    }
    client.schema.create_class(article_schema)
    print("The collection schema has been created")

# Batch import data
def batch_import_data(client, df):
    with client.batch(batch_size=10, num_workers=1) as batch:
        for i, row in df.iterrows():
            document_object = {
            "h1": row["H1"],
            "h2": row["H2"],
            "paragraph": row["Paragraph"],
            "archive": row["Archive"],
            "page_text": row["page_text"],
            "page_archive": row["page_archive"],
            "page_archive_split": row["page_archive_split"],

        }
            batch.add_data_object(document_object, class_name="Documents")

# Perform a semantic search
def semantic_search(client, query):
    nearText = {
        "concepts": [query]
    }
    properties = [
        "h1", "h2", "paragraph", "archive", "page_text", "page_archive","page_archive_split",
        "_additional {distance}"
    ]

    response = (
        client.query
        .get("Documents", properties)
        .with_near_text(nearText)
        .with_limit(10)
        .do()
    )
    return response['data']['Get']['Documents']

def print_result(result):
    for item in result:
        # Header and Subheader with their respective values
        print(f"\033[95mHeader:\033[0m {item['h1']} \n\033[95mSubheader:\033[0m {item['h2']}, \033[95mdistance metric:\033[0m {item['_additional']['distance']}")

        # Page text, archive, and archive split with their respective values
        print(f"\033[95mpage_text:\033[0m \033[4m{item['page_text']}\033[0m  \033[95mpage_archive:\033[0m \033[4m{item['page_archive']}\033[0m \033[95mpage_archive_split:\033[0m \033[4m{item['page_archive_split']}\033[0m \n")

        # Paragraph and Archive with their respective values
        print(f"\033[95mParagraph:\033[0m {item['paragraph']}")
        print(f"\033[95mArchive:\033[0m {item['archive']}")

        print('-' * 80)


if __name__ == "__main__":

    # Configuration
    openai_api_key = os.getenv("OPENAI_API_KEY") 
    cohere_api_key = os.getenv("COHERE_API_KEY")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

    client = initialize_client()
    delete_existing_schema(client)

    create_schema(client)

    df = pd.read_csv('/content/indvandring-test-v1 - Sheet1.csv')
    df = df.fillna('-')
    batch_import_data(client, df)

    query = """
    Hur var utlänningskontrollen organiserad i början?
    """

    query_result = semantic_search(client, query)

    print_result(query_result)

