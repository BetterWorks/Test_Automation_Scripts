from parser.data_parser import generate_data
import csv
import pandas as pd

def save_data_to_csv(filename, data):
    if data and isinstance(data, list): 
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data generation complete. {filename}")
    else:
        print("No data to write")  
    

if __name__ == "__main__":
    department_data = generate_data("department", 2)
    save_data_to_csv('department_data.csv', department_data)

    user_data = generate_data("user", 2)
    save_data_to_csv('user_data.csv', user_data)

    goals_data = generate_data("goals", 2)
    save_data_to_csv('goals_data.csv', goals_data)

    feedback_data = generate_data("feedbacks", 2)
    save_data_to_csv('feedback_data.csv', feedback_data)

