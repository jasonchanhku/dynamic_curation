import streamlit as st
import time
import numpy as np
from dynamic_curation import search_query

st.title('Search Markdown Content')

search_query_input = st.text_input('Enter search query')

if search_query_input:
    results = search_query(search_query_input)
    for result in results:
        #print(result.keys())
        st.write(f"Document: {result['filepath']}, \nScore: {result['@search.score']}")
        st.write(result['content'])
        st.write("----")