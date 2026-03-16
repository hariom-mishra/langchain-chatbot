import streamlit as st
from langgraph_database_backend import chatBot, checkpointer
from langchain_core.messages import HumanMessage
import uuid

##################################utils#####################################
#generate new thread id
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

#retain all threads
def save_thread(thread_id):
    if thread_id not in st.session_state["threads"]:
        st.session_state["threads"].append(thread_id)

def retrive_all_threads():
    all_threads = set()
    for checkpoints in checkpointer.list(None):
        all_threads.add(checkpoints.config["configurable"]["thread_id"])
    return list(all_threads)

#set conversation messages
def get_convo_messages(thread_id):
    CONFIG = {"configurable": {"thread_id": thread_id}}
    return chatBot.get_state(config=CONFIG).values.get("messages", [])

#reset chat
def reset_chat():
    new_thread_id = generate_thread_id()
    st.session_state["thread_id"] = new_thread_id
    save_thread(new_thread_id)
    st.session_state["message_history"] = []

##########################################session setup######################
#initialize message history
if 'message_history' not in st.session_state:
    st.session_state["message_history"] = []

#assign thread id to conversation
if "thread_id" not in st.session_state:
    new_thread_id = generate_thread_id()
    st.session_state["thread_id"] = new_thread_id

if "threads" not in st.session_state:
        st.session_state["threads"] = retrive_all_threads()

save_thread(st.session_state["thread_id"])

######################################ui#####################################
#sidebar ui
st.sidebar.title("LangGraph ChatBot")
if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("My Conversation")
for thread_id in st.session_state["threads"]:
    if st.sidebar.button(str(thread_id)):
        print("getting called..")
        st.session_state["thread_id"] = thread_id
        messages = get_convo_messages(thread_id)
        temp_message = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_message.append({"role": role, "content": message.content})
        print(temp_message)
        st.session_state["message_history"] = temp_message

#show messages
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

#input section
user_input = st.chat_input("Type here...")
#create config
CONFIG = {
    "configurable": {"thread_id": st.session_state["thread_id"]},
    "metadata": {"thread_id": st.session_state["thread_id"]},
    "run_name": "chat_turn"
    }

if user_input:
    #show humna message
    st.session_state.message_history.append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    #stream ai message
    with st.chat_message('assistant'):
        ai_message =st.write_stream(
            message_chunk.content for message_chunk, metadata in chatBot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )
    #save the ai message 
    st.session_state.message_history.append({'role': 'assistant', 'content': ai_message})
