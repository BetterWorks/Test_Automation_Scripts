feedbacks_prompt = ('''YOU ARE A WORLD-CLASS DATA GENERATOR, TASKED WITH CREATING REALISTIC FEEDBACK FOR EMPLOYEES AT A FICTITIOUS PHARMACEUTICAL COMPANY NAMED "BETTERPHARMA". THE FEEDBACK WILL BE BASED ON THE EMPLOYEES' PERFORMANCE IN ACHIEVING THEIR GOALS AND COLLABORATING WITH TEAM MEMBERS.

FOR EACH EMPLOYEE, YOU WILL GENERATE THE FOLLOWING:

1. Feedback question: The question or criteria being assessed. Examples might include:
   - How effectively did the employee meet regulatory compliance standards?
   - How well did the employee communicate project updates?
   - Did the employee demonstrate leadership in driving team performance?
   - How innovative was the employee in solving industry-specific problems?
   - Was the employee punctual and reliable in delivering tasks?
2. From user: The email address of the person giving the feedback (e.g., the manager, peer, or skip-level manager).
3. For user: The email address of the person receiving the feedback.
4. Feedback answer: A realistic assessment of the employee's performance based on the goal's progress, interpersonal interactions, and results. The feedback should be constructive and specific to the user's role and responsibilities.

FEEDBACK SHOULD INCLUDE EVALUATIONS ON:
- **Communication**
- **Quality of Work**
- **Teamwork**
- **Problem-Solving**
- **Punctuality**
- **Leadership**
- **Innovation**

JSON OUTPUT FORMAT:

    "feedbacks": [
        
    ]

DIVERSIFY FEEDBACK SOURCES (MANAGERS, PEERS, SKIP-LEVEL MANAGERS), AND TAILOR COMMENTS TO THE EMPLOYEE'S ROLE AND SPECIFIC GOALS.

THE FEEDBACK SHOULD REFLECT REALISTIC INTERACTIONS, FOCUSING ON THE EMPLOYEE'S PERFORMANCE IN ACHIEVING GOALS AND THEIR CONTRIBUTIONS TO DEPARTMENTAL SUCCESS. Return only the raw JSON data inside triple backticks. No explanation, no additional sentences.''')