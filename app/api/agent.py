from langchain_openai import ChatOpenAI

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from app.api.core.database.db import get_students  # Fetch student data
import os
from langchain_groq import ChatGroq
import json

with open("faq.json", "r") as file:
    FAQ_DATA = json.load(file)

# ✅ Load API key from environment variables
os.environ["GROQ_API_KEY"] = "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"  # Replace with your actual key

# Initialize Groq model
llm = ChatGroq(model_name="llama3-8b-8192")  # You can also try "mixtral-8x7b-32768"


# ✅ Function to get student details from the database(RAG)
def get_student_info(name: str):
    students = get_students()
    for student in students:
        if student["name"].lower() == name.lower():
            return student
    return None  # Return None if student is not found

# ✅ Function to process queries
def run_agent(query: str):
    query = query.strip().lower()

    if query in FAQ_DATA:
        return FAQ_DATA[query] 

    # If query is about a student, fetch from DB
    if "student" in query or "details" in query or "tell me about" in query:
        name = query.split("about")[-1].strip()
        if name:
            student_data = get_student_info(name)
            if student_data:
                return f"Here is the information for {name}: {student_data}"
            return f"Sorry, no student named {name} was found."
        return "Please specify a student name."

    # Otherwise, process general queries using LangChain
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=query)
    ]
    
    response = llm(messages)  # Get response from LangChain LLM
    return response.content  # Return AI response
