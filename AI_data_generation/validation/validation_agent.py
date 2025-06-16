def validate_data(user_data, department_data, goals_data, feedback_data):
    assert user_data['email'].is_unique, "User emails must be unique"
    assert department_data['department_id'].is_unique, "Department IDs must be unique"

    # Example: Ensure each goal has a valid owner in user_data
    for email in goals_data['owner_email']:
        assert email in user_data['email'].values, f"Goal owner {email} not found in user data"
    
    print("Validation passed.")
