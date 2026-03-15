from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

model = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

graph = StateGraph(ChatState)

#checkpointer
con = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=con)

def chat_node(state: ChatState) -> ChatState:
    output = model.invoke(state["messages"])
    return {"messages": output}

#define nodes
graph.add_node("chat_node", chat_node)

#define edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatBot = graph.compile(checkpointer=checkpointer)