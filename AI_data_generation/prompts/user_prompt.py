user_prompt = ('''YOU ARE A WORLD-CLASS DATA GENERATOR, TASKED WITH CREATING REALISTIC USER PROFILES FOR A PHARMACEUTICAL COMPANY NAMED "BETTERPHARMA". GENERATE TOTAL OF {n} DETAILED USERS PROFILES IN JSON FORMAT WITH THE FOLLOWING FIELDS:

1. id: A unique identifier for each user.
2. email: The user's email address.
3. first_name: The user's first name.
4. last_name: The user's last name.
5. department_name: The department to which the user belongs (Marketing, Engineering, Sales, HR).
6. title: The user's role or title (CEO, CTO, CFO, etc.).
7. phone: The user's phone number.
8. deactivation_date: If the user is inactive, include their deactivation date.
9. hire_date: The user's hire date.
10. manager_email: The email address of the user's manager.
11. location: The location where the user is based (e.g., India, Europe, USA).
12. locale: The user's preferred language/locale.
13. preferred_name: The user's preferred name, if applicable.
14. on_leave: Boolean field indicating whether the user is on leave (True or False).
15. matrix_manager: If the user has a skip level manager, include the skip level manager's email.
16. All users will have the password "test@1234".

THE DATA MUST BE REALISTIC FOR A BUSINESS ENVIRONMENT, REFLECTING THE HIERARCHICAL STRUCTURE AND FUNCTIONS OF A PHARMACEUTICAL COMPANY.

Generate data for TOTAL {n} employees**, evenly distributed across four departments: **Marketing**, **Engineering**, **Sales**, and **HR**. The hierarchy should include various levels (e.g., CEO, CTO, Managers, Team Leads, and Individual Contributors). Each user must have a realistic role and reporting structure, with managers and matrix managers where applicable. Return only the raw JSON data inside triple backticks. No explanation, no additional sentences.''')
