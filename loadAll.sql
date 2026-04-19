USE car_dealership;

-- Divisions
INSERT INTO DIVISION (division_id, division_name, description) VALUES
(1, 'Sales', 'Handles all vehicle sales operations'),
(2, 'Maintenance Services', 'Handles vehicle maintenance and repair'),
(3, 'Financial Services', 'Handles loans, financing and accounting');


-- Departments
INSERT INTO DEPARTMENT (department_id, department_name, description, status, division_id) VALUES
(1, 'Dealers New Car Sales', 'Sells brand new vehicles from dealers', 'Active', 1),
(2, 'Dealers Used Car Sales', 'Sells used vehicles from dealers', 'Active', 1),
(3, 'Online Used Car Sales', 'Sells used vehicles through online platform', 'Active', 1),
(4, 'Sales Administration', 'Manages sales records and reporting', 'Active', 1),
(5, 'Maintenance Services', 'Performs vehicle maintenance and repairs', 'Active', 2),
(6, 'Parts Department', 'Manages parts inventory for maintenance', 'Active', 2),
(7, 'Financial Services and Loans', 'Processes vehicle financing and loans', 'Active', 3),
(8, 'Accounting', 'Manages financial records and reporting', 'Active', 3),
(9, 'Customer Finance Support', 'Assists customers with financing options', 'Active', 3),
(10, 'Internal Audit', 'Audits financial and sales operations', 'Active', 3);


-- Roles
INSERT INTO ROLE (role_id, role_name) VALUES
(1, 'Administrator'),
(2, 'Sales Staff'),
(3, 'Service Staff'),
(4, 'Finance Staff'),
(5, 'Accountant');


-- Employees
INSERT INTO EMPLOYEE (employee_id, first_name, last_name, emp_email, emp_phone, hire_date, salary, position, department_id) VALUES
(1, 'James', 'Carter', 'jcarter@dealership.com', '301-555-0101', '2020-03-15', 55000.00, 'Sales Manager', 1),
(2, 'Maria', 'Lopez', 'mlopez@dealership.com', '301-555-0102', '2019-07-22', 48000.00, 'Sales Associate', 2),
(3, 'David', 'Kim', 'dkim@dealership.com', '301-555-0103', '2021-01-10', 47000.00, 'Sales Associate', 3),
(4, 'Sandra', 'Brown', 'sbrown@dealership.com', '301-555-0104', '2018-11-05', 52000.00, 'Senior Technician', 5),
(5, 'Kevin', 'Nguyen', 'knguyen@dealership.com', '301-555-0105', '2022-06-01', 45000.00, 'Technician', 5),
(6, 'Rachel', 'Adams', 'radams@dealership.com', '301-555-0106', '2020-09-14', 60000.00, 'Loan Officer', 7),
(7, 'Michael', 'Turner', 'mturner@dealership.com', '301-555-0107', '2017-04-30', 70000.00, 'Accountant', 8),
(8, 'Linda', 'Harris', 'lharris@dealership.com', '301-555-0108', '2023-02-20', 43000.00, 'Finance Support', 9),
(9, 'Chris', 'Johnson', 'cjohnson@dealership.com', '301-555-0109', '2016-08-11', 80000.00, 'Administrator', 10),
(10, 'Emily', 'White', 'ewhite@dealership.com', '301-555-0110', '2021-05-18', 46000.00, 'Parts Coordinator', 6);


-- Users
INSERT INTO USER (user_id, username, password, employee_id, role_id) VALUES
(1, 'jcarter', 'hashed_pw_1', 1, 2),
(2, 'mlopez', 'hashed_pw_2', 2, 2),
(3, 'dkim', 'hashed_pw_3', 3, 2),
(4, 'sbrown', 'hashed_pw_4', 4, 3),
(5, 'knguyen', 'hashed_pw_5', 5, 3),
(6, 'radams', 'hashed_pw_6', 6, 4),
(7, 'mturner', 'hashed_pw_7', 7, 5),
(8, 'lharris', 'hashed_pw_8', 8, 4),
(9, 'cjohnson', 'hashed_pw_9', 9, 1),
(10, 'ewhite', 'hashed_pw_10', 10, 3);


-- these should fail due to constraints

-- department with a division that doesn't exist
-- INSERT INTO DEPARTMENT (department_id, department_name, description, status, division_id)
-- VALUES (11, 'Ghost Department', 'No division', 'Active', 99);

-- duplicate username
-- INSERT INTO USER (user_id, username, password, employee_id, role_id)
-- VALUES (11, 'jcarter', 'hashed_pw_11', 1, 2);

-- employee with invalid department
-- INSERT INTO EMPLOYEE (employee_id, first_name, last_name, emp_email, emp_phone, hire_date, salary, position, department_id)
-- VALUES (11, 'Ghost', 'User', 'ghost@dealership.com', '000-000-0000', '2024-01-01', 30000.00, 'None', 99);
