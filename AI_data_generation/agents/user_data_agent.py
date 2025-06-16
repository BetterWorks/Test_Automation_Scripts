import re
import json
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from prompts.user_prompt import user_prompt

# Initialize Ollama 
llm = OllamaLLM(model="llama3")

# Define the function to generate user data using the prompt
def generate_user_data(n=10):  # Set a default value of 10 if n is not provided
    # Format the prompt template with the given n or default to 10
    user_prompt_template = user_prompt.format(n=n)
    
    if not user_prompt_template:
        return []

    # Initialize the prompt
    prompt = PromptTemplate(input_variables=["n"], template=user_prompt_template)
    user_chain = prompt | llm  # Using the `RunnableSequence`

    users = []
    try:
        # Generate the data using the AI model
        generated_data = user_chain.invoke({})
        print(f"Generated data: {generated_data}")

        generated_data = generated_data.strip('`')

        # Attempt direct JSON parsing if the model response is JSON
        try:
            user_data = json.loads(generated_data)
            users.extend(user_data.get("users", []))  # Extend users with list of dictionaries if valid JSON
        except json.JSONDecodeError:
            # Fallback: use regex to find JSON between backticks if JSON parsing fails
            match = re.search(r'```(.*?)```', generated_data, re.DOTALL)
            if match:
                data_str = match.group(1).strip()
                data_str = data_str.replace("'", '"')
                user_data = json.loads(data_str)
                users.extend(user_data.get("users", []))
            else:
                print("Failed to extract JSON from the generated data.")
                
    except Exception as e:
        print(f"Error generating user data: {e}")

    return users

