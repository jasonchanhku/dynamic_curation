import os
import streamlit as st
st.set_page_config(layout="wide")
# Additional imports will be needed to interact with Azure Blob Storage and Azure Search.

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from dotenv import load_dotenv
import time
from data_prep import update_search_index

load_dotenv()


CONNECTION_STRING = os.getenv('AZURE_BLOB_STORAGE_CS')

CONTAINER_NAME = os.getenv('AZURE_BLOB_STORAGE_CONTAINER_NAME')
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(CONNECTION_STRING)

AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME')
AZURE_SEARCH_ADMIN_KEY = os.getenv('AZURE_SEARCH_ADMIN_KEY')


# Functions to interact with Azure Blob Storage and Azure Search

# function to get blob content
def get_blob_content(blob_name):
    blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    return blob_client.download_blob().readall()

# function to list blobs
def list_blobs():
    # List the blobs in the container.
    return BLOB_SERVICE_CLIENT.get_container_client(CONTAINER_NAME).list_blobs()

# function to upload a blob
def upload_blob(blob_name, data):
    blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    blob_client.upload_blob(data, overwrite=True)

# function to search indexed blobs using Azure Search
def search_query(query):
    search_client = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT, index_name=AZURE_SEARCH_INDEX_NAME, credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY))
    
    results = search_client.search(search_text=query)
    
    return results

# Streamlit app pages
def page_blob_interaction():
    st.title('Markdown File Browser & Editor')
    
    # list all md files
    blobs = list(list_blobs())
    md_files = [blob.name for blob in blobs if blob.name.endswith('.md')]
    selected_file = st.selectbox('Select a markdown file', md_files)
    col1, col2 = st.columns(2)
    # show in selectbox
    
    
    if selected_file:
        file_content = get_blob_content(selected_file).decode("utf-8")
        print(f"chosen {selected_file}")
        with col1:
            st.header("Markdown Editor")
            edited_content = st.text_area("File content", value=file_content, height=600)
            if st.button('Save and Upload'):
                upload_blob(selected_file, edited_content.encode("utf-8"))
                st.success('File Uploaded and Saved.')
                # Call index function whenever a file is uploaded after editing
                time.sleep(5)
                update_search_index(selected_file)
                st.success('Search Index Updated. Please wait ~20s to reflect changes')
        with col2:
            st.header("Markdown Preview")
            st.markdown(edited_content)


def page_search():
    st.title('Search Markdown Content')
    
    search_query_input = st.text_input('Enter search query')
    
    if search_query_input:
        results = search_query(search_query_input)
        for result in results:
            #print(result.keys())
            st.write(f"Document: {result['filepath']}, \nScore: {result['@search.score']}")
            st.write(result['content'])
            st.write("----")


# Set up streamlit page structure
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Browse and Edit Markdown", "Search Markdown Content"])

if page == "Browse and Edit Markdown":
    page_blob_interaction()
elif page == "Search Markdown Content":
    page_search()