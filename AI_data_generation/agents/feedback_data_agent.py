import re
import json
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from prompts.feedback_prompt import feedbacks_prompt

# Initialize Ollama 
llm = OllamaLLM(model="llama3")
# Define the function to generate feedbacks data using the prompt
def generate_feedbacks_data(n=10):
    feedbacks_prompt_template = feedbacks_prompt.format(n=n)
    prompt = PromptTemplate(input_variables=["n"], template=feedbacks_prompt_template)
    feedbacks_chain = prompt | llm
    
    feedbacks = []
    try:    
        # Generate the data using the AI model
        generated_data = feedbacks_chain.invoke({})
        print(f"Generated Data: {generated_data}")

        generated_data = generated_data.strip('`')
            
        try:
            feedbacks_data = json.loads(generated_data)
            feedbacks.extend(feedbacks_data.get("feedbacks", []))
                # Use regex to find the content between triple backticks
        except json.JSONDecodeError:
            # Fallback: use regex to find JSON between backticks if JSON parsing fails
            match = re.search(r'```(.*?)```', generated_data, re.DOTALL)
            if match:
                data_str = match.group(1).strip()
                data_str = data_str.replace("'", '"')
                user_data = json.loads(data_str)
                feedbacks.extend(user_data.get("feedbacks", []))
            else:
                print("Failed to extract JSON from the generated data.") # Convert the string to JSON and append to the list
    except Exception as e:
        print(f"Error generating feedbacks data: {e}")

    
    return feedbacks

