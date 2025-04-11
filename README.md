Functional database for eshop Svet-puzzle.sk
------------------------------------------

Technology used:
--------------------------------------------
SQL, Python, Flask app HTML, PostgreSQL 

Abstract:
-------------------------------------------
This project is for my diploma thesis Functional database for eshop Svet-puzzle.sk, and marketing analyse for them 

The project includes:
-----------------------------------------------------------------------------------------------------------------------
Creating a database and multiple related tables
Adding, editing, and managing both data and table structure
Defining primary and foreign keys to establish relationships between tables
Validating data and correcting relational issues
Performing basic data operations, including marketing-related queries
Building a web interface to view any table using SELECT * FROM table_name
Implementing navigation between multiple subpages
Creating a subpage that calculates KPIs such as profit, costs, and income
Providing a form to insert new records into the database
Adding functionality to delete records from the database via the web interface



 Conceptual, logical, and physical models (Constellation Schema)
----------------------------------------------------------------------------------------------------------------------------------------------------------------
![model](https://github.com/user-attachments/assets/499b3d95-37b2-40c3-8004-cafdcf43c001)
![logic_model](https://github.com/user-attachments/assets/c5994ee0-49fe-4f52-baed-a4b7ddd66308)
![f_model](https://github.com/user-attachments/assets/870ad322-60e5-42e5-a004-c172af25c031)

The process of creating the database and tables with customers, products and orders was performed using PostgreSQL and stored in file 
[postgre_git.docx](https://github.com/user-attachments/files/19274187/postgre_git.docx)



Set up backend python + connection to database PostgreSQL
-------------------------------------------------------------
flask_app/app.py

web interface to view any table using SELECT * FROM table_name
------------------------------
flask_app/templates/index.html
![image](https://github.com/user-attachments/assets/89504f9d-559f-412e-9973-1d4879e0aac0)
![image](https://github.com/user-attachments/assets/1f9a7eca-6464-4fbd-bf4a-77066483b521)

Subpage that calculates KPIs such as profit, costs, and income/ Analyse
------------------------------
flask_app/templates/select.html

![image](https://github.com/user-attachments/assets/342f234f-fbff-447e-979e-01b3ba9cfbed)
Users can select specific filters to view income, expenses, and profit based on chosen indicators
It's possible to filter data by year (2022, 2023, or 2024)
Users can also choose whether to display data for legal entities or individuals
If no filters are selected, the form will automatically include all available data without restrictions

![image](https://github.com/user-attachments/assets/c7aed052-e971-4693-a7f3-e628036d7342)

Form to insert new records into the database
---------------------------------------------
flask_app/templates/form.html
Users first select the target table where they want to insert data
A form is then displayed, allowing users to fill in all required fields
If a value is entered that already exists in a primary key column, the system will display an error message
Similarly, if a foreign key references a primary key that doesn’t yet exist, the program will notify the user with a warning message

![image](https://github.com/user-attachments/assets/b8c7003d-f39e-401b-a847-389525083198)



Delete records from the database via the web interface
------------------------------------------------------
flask_app/templates/delete.html
Users first select the target table from which they want to delete data
They are then prompted to enter the ID (i.e., the primary key) of the row they wish to delete
If the selected row is referenced by foreign keys in other tables, an error message is displayed, and the user must first delete related rows from those tables
An error is also shown if the entered ID does not exist in the selected table
If no issues are detected, the row is successfully deleted from the database


![image](https://github.com/user-attachments/assets/5e0ff6e5-6495-430f-8d40-d543e3c1c9e7)








Summary
--------------------
This project was created as part of a diploma thesis and served as practical experience in SQL and Python development











