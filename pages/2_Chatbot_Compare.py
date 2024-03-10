import streamlit as st
from datetime import datetime
from azure_chatbot import AzureChatbot
import os
from distutils.util import strtobool

DEFAULT_MODEL = "Azure"
RAW_MODEL = "Azure_raw"

# make model an option and put COST_PER_TOKEN under states
COSTING_MAP = {
    "gpt-3.5-turbo": 0.000002,
    "gpt-4": 0.00006
}

MODEL_FACTORY = {
    "Azure": AzureChatbot,
    "Azure_raw": AzureChatbot
}


print("Clicked English page")

#st.image("./assets/images/manulife_logo_cropped.png", width=220)

st.title("HKIRD eAOM Chatbot 🤖")


def on_button_click():
    del st.session_state["messages"]
    del st.session_state["raw_messages"]

if "messages" not in st.session_state:
    print("no messages detected, initializing states")
    st.session_state.messages = []
    st.session_state.raw_messages=[]
    # Assume default chatbot is azure
    st.session_state.model = "Azure"
    #st.session_state.chatbot = MODEL_FACTORY["Azure"]
    st.session_state.llm_model = "gpt-4"
    

with st.form("my_form"):
   st.write("Inside the form")
   my_query = st.text_input('Your Question Here')

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")

col1, col2 = st.columns(2)


with col1:
# code block for chat history
    st.title("raw chatbot")
    for message in st.session_state["raw_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            # printing out citations if exists
            if "citations" in message.keys():
                print("citations detected")
                # expander version
                for index, message_citation in enumerate(message["citations"]):
                    with st.expander(f"[{index+1}] {message_citation['filepath']}"):
                        st.markdown(message_citation["content"])


    # code block for user input
    if submitted:
        user_prompt = my_query
        user_messages = {"role": "user", "content": user_prompt}
        st.session_state.raw_messages.append(user_messages)


        with st.chat_message("user"):
            st.markdown(user_prompt)

        # create an instance of ChatResponseGenerator
        response_generator = st.session_state.chatbot(
            idx_var="AZURE_SEARCH_INDEX_NAME_RAW",
            conversation=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.raw_messages
                ]
        )

        # generate responses
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # streaming mode in a for loop
            for partial_response in response_generator.response_stream():
                full_response += partial_response if partial_response is not None else ""
                message_placeholder.markdown(full_response + "▌")

            full_response = response_generator.preprocess_response(full_response)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)

            assistant_messages = {"role": "assistant", "content": full_response}

            # citation handling
            message_citations = response_generator.citations

            if len(message_citations) > 0:
                assistant_messages["citations"] = response_generator.citations

                # expander version
                for index, message_citation in enumerate(message_citations):
                    with st.expander(f"[{index+1}] {message_citation['filepath']}"):
                        st.markdown(message_citation["content"])


        st.session_state.raw_messages.append(assistant_messages)


with col2:
    # code block for chat history
    st.title("curated chatbot")
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            # printing out citations if exists
            if "citations" in message.keys():
                print("citations detected")
                # expander version
                for index, message_citation in enumerate(message["citations"]):
                    with st.expander(f"[{index+1}] {message_citation['filepath']}"):
                        st.markdown(message_citation["content"])


    # code block for user input
    if submitted:
        user_prompt = my_query
        user_messages = {"role": "user", "content": user_prompt}
        st.session_state.messages.append(user_messages)


        with st.chat_message("user"):
            st.markdown(user_prompt)

        # create an instance of ChatResponseGenerator
        response_generator = st.session_state.chatbot(
            idx_var="AZURE_SEARCH_INDEX_NAME",
            conversation=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
        )

        # generate responses
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # streaming mode in a for loop
            for partial_response in response_generator.response_stream():
                full_response += partial_response if partial_response is not None else ""
                message_placeholder.markdown(full_response + "▌")

            full_response = response_generator.preprocess_response(full_response)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)

            assistant_messages = {"role": "assistant", "content": full_response}

            # citation handling
            message_citations = response_generator.citations

            if len(message_citations) > 0:
                assistant_messages["citations"] = response_generator.citations

                # expander version
                for index, message_citation in enumerate(message_citations):
                    with st.expander(f"[{index+1}] {message_citation['filepath']}"):
                        st.markdown(message_citation["content"])


        st.session_state.messages.append(assistant_messages)
    

with st.sidebar:
    st.session_state.chatbot = MODEL_FACTORY[DEFAULT_MODEL]
    st.button("Clear Chat History and Tokens", on_click=on_button_click)
    st.markdown("""
    
    ### Introduction
    - This is a Dynamic Curation tool to compare before and after impact of document curation
    - Original document is the .pdf version and curation version is the .md version
                
    ### Remarks
    - Aim is to speed up document curation and feedback loop
    - All in one place, no need to manually download/edit/reupload/reindex

    """)