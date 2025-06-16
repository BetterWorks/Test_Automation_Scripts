import re
import json
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from prompts.goals_prompt import goals_prompt

# Initialize Ollama 
llm = OllamaLLM(model="llama3")
# Define the function to generate goals data using the prompt
def generate_goals_data(n=10):
    goals_prompt_template = goals_prompt.format(n=n)
    prompt = PromptTemplate(input_variables=["n"], template=goals_prompt_template)
    goals_chain = prompt | llm
    
    goals = []
    try:    
        # Generate the data using the AI model
        generated_data = goals_chain.invoke({})
        print(f"Generated Data: {generated_data}")

        generated_data = generated_data.strip('`')
            
        try:
            goals_data = json.loads(generated_data)
            goals.extend(goals_data.get("goals", []))
                # Use regex to find the content between triple backticks
        except json.JSONDecodeError:
            # Fallback: use regex to find JSON between backticks if JSON parsing fails
            match = re.search(r'```(.*?)```', generated_data, re.DOTALL)
            if match:
                data_str = match.group(1).strip()
                data_str = data_str.replace("'", '"')
                user_data = json.loads(data_str)
                goals.extend(user_data.get("goals", []))
            else:
                print("Failed to extract JSON from the generated data.") # Convert the string to JSON and append to the list
    except Exception as e:
        print(f"Error generating goals data: {e}")

    
    return goals

