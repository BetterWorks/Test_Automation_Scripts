department_prompt = ('''YOU ARE A WORLD-CLASS DATA GENERATOR, TASKED WITH CREATING INDUSTRY-SPECIFIC DEPARTMENTAL DATA FOR A FICTITIOUS PHARMACEUTICAL COMPANY NAMED "BETTERPHARMA". YOU WILL DEFINE {n} DEPARTMENTS and it's parent department. 

FOR EACH DEPARTMENT, YOU WILL GENERATE THE FOLLOWING:

1. name: The name of the department (e.g., Marketing, Engineering, Sales, HR).
2. is_active: true for active
3. parent: Parent department should be exsiting, so it can be in row as department and in next row as parent for other department.
GENERATE DATA FOR **{n} DEPARTMENTS** Ensure the goals are realistic and aligned with the pharmaceutical industry's needs and operations. Return only the raw JSON data inside triple backticks. No explanation, no additional sentences.''')