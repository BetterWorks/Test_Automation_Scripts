import re
import json
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from prompts.department_prompt import department_prompt

# Initialize Ollama 
llm = OllamaLLM(model="llama3")
# Define the function to generate department data using the prompt
def generate_department_data(n=10):
    department_prompt_template = department_prompt.format(n=n)
    prompt = PromptTemplate(input_variables=["n"], template=department_prompt_template)
    department_chain = prompt | llm
    
    departments = []
    try:    
        # Generate the data using the AI model
        generated_data = department_chain.invoke({})
        print(f"Generated Data: {generated_data}")

        generated_data = generated_data.strip('`')
            
        try:
            department_data = json.loads(generated_data)
            departments.extend(department_data.get("Departments", []))
                # Use regex to find the content between triple backticks
        except json.JSONDecodeError:
            # Fallback: use regex to find JSON between backticks if JSON parsing fails
            match = re.search(r'```(.*?)```', generated_data, re.DOTALL)
            if match:
                data_str = match.group(1).strip()
                data_str = data_str.replace("'", '"')
                user_data = json.loads(data_str)
                departments.extend(user_data.get("Departments", []))
            else:
                print("Failed to extract JSON from the generated data.") # Convert the string to JSON and append to the list
    except Exception as e:
        print(f"Error generating department data: {e}")

    
    return departments

