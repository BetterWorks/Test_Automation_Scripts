goals_prompt = '''YOU ARE A WORLD-CLASS DATA GENERATOR, TASKED WITH CREATING INDUSTRY-SPECIFIC {n} GOALS FOR EMPLOYEES AT A FICTITIOUS PHARMACEUTICAL COMPANY NAMED "BETTERPHARMA". THESE GOALS WILL BE ALIGNED WITH EACH EMPLOYEE'S DEPARTMENT AND ROLE.

FOR EACH EMPLOYEE, YOU WILL GENERATE THE FOLLOWING MENDATORY FIELDS:

1. Goal name: A detailed description of the goal, including tasks and expectations.
2. Type: Whether it is a goal or milestone.
3. Progress: The current percentage completion of the goal (e.g., 65%).
4. Start date: The date when the goal was set.
5. End date: The target date for completing the goal.
6. Owner email: The email of the employee to whom the goal is assigned.
7. Categories: A list of categories or areas the goal aligns with (e.g., Pharma_Engineering, Sales_Targets).
8. Description: A detailed description of the goal, including tasks and expectations, empty in case of milestone.
9. Private: Boolean field indicating whether the goal is private or public, empty in case of milestone.

THE GOALS SHOULD ALIGN WITH THE DEPARTMENT'S/TEAM/COMPANY/FEEDBACKS FOCUS. FOR EXAMPLE:
- **MARKETING**: Goals should relate to campaigns, product awareness, and customer engagement.
- **ENGINEERING**: Goals should focus on product development, IT systems, and automation.
- **SALES**: Goals should focus on client relationships, sales targets, and product sales.
- **HR**: Goals should focus on recruitment, employee engagement, and work culture.

JSON OUTPUT FORMAT:

    "goals": [
        
    ]


GENERATE DATA, WITH INDUSTRY-RELEVANT TOTAL {n} GOALS THAT INCLUDE SPECIFIC MILESTONES AND MEASURABLE OBJECTIVES. Return only the raw JSON data inside triple backticks. No explanation, no additional sentences.
'''
