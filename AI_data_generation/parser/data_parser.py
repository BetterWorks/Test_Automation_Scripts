import re
import json
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from prompts.feedback_prompt import feedbacks_prompt
from prompts.user_prompt import user_prompt
from prompts.department_prompt import department_prompt
from prompts.goals_prompt import goals_prompt

# Initialize Ollama 
llm = OllamaLLM(model="llama3")
# Define the function to generate feedbacks data using the prompt
def generate_data(feature_name, n=10):
    if feature_name == "user":
        feature_prompt = user_prompt
    elif feature_name == "department":
        feature_prompt = department_prompt
    elif feature_name == "goals":
        feature_prompt = goals_prompt
    elif feature_name == "feedbacks":
        feature_prompt = feedbacks_prompt
    else:
        return []
    
    prompt_template = feature_prompt.format(n=n)
    prompt = PromptTemplate(input_variables=["n"], template=prompt_template)
    feature_chain = prompt | llm
    
    feature = []
    try:    
        # Generate the data using the AI model
        generated_data = feature_chain.invoke({})
        print(f"Generated Data: {generated_data}")

        generated_data = generated_data.strip('`')
            
        try:
            feature_data = json.loads(generated_data)
            feature.extend(feature_data.get(f"{feature_name}", []))
                # Use regex to find the content between triple backticks
        except json.JSONDecodeError:
            # Fallback: use regex to find JSON between backticks if JSON parsing fails
            match = re.search(r'```(.*?)```', generated_data, re.DOTALL)
            if match:
                data_str = match.group(1).strip()
                data_str = data_str.replace("'", '"')
                user_data = json.loads(data_str)
                feature.extend(user_data.get(f"{feature_name}", []))
            else:
                print("Failed to extract JSON from the generated data.") # Convert the string to JSON and append to the list
    except Exception as e:
        print(f"Error generating {feature} data: {e}")

    
    return feature

