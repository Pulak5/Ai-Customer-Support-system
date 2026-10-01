# TODO: Implement module logic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.core.config import settings

# 1. Define exactly what we want the AI to extract
class TicketTriageResult(BaseModel):
    category: str = Field(description="The category: billing, technical, sales, or general")
    priority: str = Field(description="The priority: low, medium, high, or urgent")
    sentiment: str = Field(description="Customer sentiment: happy, neutral, frustrated, or angry")

def triage_ticket_text(subject: str, description: str) -> TicketTriageResult:
    # Fallback just in case you haven't put a real API key in the .env file yet
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-api-key-here":
        print(" No OpenAI API Key found. Skipping AI Triage.")
        return TicketTriageResult(category="general", priority="medium", sentiment="neutral")
        
    # 2. Initialize the LLM (using the fast and cheap GPT-4o-mini)
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)
    
    # 3. Force the LLM to output our exact Pydantic schema
    structured_llm = llm.with_structured_output(TicketTriageResult)
    
    # 4. Define the Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert customer support triage system. Analyze the ticket and extract the category, priority, and sentiment."),
        ("human", "Subject: {subject}\n\nDescription: {description}")
    ])
    
    # 5. Chain the prompt and the LLM together, then run it!
    chain = prompt | structured_llm
    result = chain.invoke({"subject": subject, "description": description})
    
    return result