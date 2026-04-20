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
INSERT INTO `USER` (user_id, username, password, employee_id, role_id) VALUES
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

-- Customers
INSERT INTO Customer (customer_name, customer_address, customer_email) VALUES
('John Doe','123 Main St','john@example.com'),
('Jane Smith','456 Oak St','jane@example.com'),
('Mike Brown','789 Pine St','mike@example.com'),
('Sara Lee','321 Elm St','sara@example.com'),
('Tom Clark','654 Maple St','tom@example.com'),
('Emma Davis','987 Cedar St','emma@example.com'),
('Chris White','147 Birch St','chris@example.com'),
('Anna Hall','258 Walnut St','anna@example.com'),
('David King','369 Cherry St','david@example.com'),
('Lisa Scott','159 Spruce St','lisa@example.com');

-- Phone Numbers
INSERT INTO PhoneNumber (phone_number, customer_id) VALUES
('111-111-1111',1), ('222-222-2222',1),
('333-333-3333',2), ('444-444-4444',3),
('555-555-5555',4), ('666-666-6666',5),
('777-777-7777',6), ('888-888-8888',7),
('999-999-9999',8), ('101-101-1010',9),
('202-202-2020',10), ('303-303-3030',1);

-- Vehicles
INSERT INTO Vehicle (vehicle_make, vehicle_model, vehicle_year, vehicle_vin, vehicle_price, vehicle_mileage, vehicle_condition, vehicle_availability_status) VALUES
('Toyota','Camry',2022,'VIN001',25000,10000,'used','available'),
('Honda','Civic',2023,'VIN002',27000,5000,'used','available'),
('Ford','F150',2021,'VIN003',35000,20000,'used','maintenance'),
('Tesla','Model3',2024,'VIN004',45000,0,'new','available'),
('BMW','X5',2022,'VIN005',60000,15000,'used','sold'),
('Audi','A4',2023,'VIN006',42000,7000,'used','available'),
('Nissan','Altima',2020,'VIN007',20000,30000,'used','available'),
('Hyundai','Elantra',2021,'VIN008',22000,18000,'used','available'),
('Kia','Sorento',2022,'VIN009',30000,12000,'used','sold'),
('Chevy','Malibu',2023,'VIN010',26000,8000,'used','available');

-- Sales
INSERT INTO Sale (sale_date, sale_price, financing_option, payment_method, vehicle_id, customer_id, department_id, employee_id) VALUES
('2024-01-01',24000,'loan','bank_transfer',1,1,1,1),
('2024-01-05',26000,'cash','cash',2,2,1,2),
('2024-02-10',34000,'lease','credit_card',3,3,2,3),
('2024-02-15',45000,'loan','debit_card',4,4,3,4),
('2024-03-01',58000,'cash','cash',5,5,1,1),
('2024-03-10',41000,'loan','bank_transfer',6,6,2,3),
('2024-04-01',19000,'cash','cash',7,7,1,2),
('2024-04-15',21000,'lease','credit_card',8,8,3,4),
('2024-05-01',29000,'loan','debit_card',9,9,1,1),
('2024-05-10',25000,'cash','cash',10,10,2,3);

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



INSERT INTO SERVICE (service_type, service_date, service_cost, customer_id, vehicle_id, employee_id, department_id) VALUES
('Oil Change','2024-06-01',80,1,1,4,5),
('Brake Repair','2024-06-02',300,2,2,5,5),
('Engine Check','2024-06-03',150,3,3,4,5),
('Tire Replacement','2024-06-04',400,4,4,5,5),
('Battery Replacement','2024-06-05',200,5,5,4,5),
('Transmission Fix','2024-06-06',1200,6,6,5,5),
('Alignment','2024-06-07',100,7,7,4,5),
('AC Repair','2024-06-08',350,8,8,5,5),
('Inspection','2024-06-09',90,9,9,4,5),
('Detailing','2024-06-10',180,10,10,5,5);


INSERT INTO SERVICE_PART (part_name, quantity, part_cost, service_id) VALUES
('Oil Filter',1,20,1),
('Brake Pad',4,100,2),
('Spark Plug',4,60,3),
('Tire',4,300,4),
('Battery',1,150,5),
('Transmission Fluid',2,200,6),
('Alignment Kit',1,50,7),
('AC Compressor',1,250,8),
('Inspection Kit',1,30,9),
('Cleaning Kit',1,40,10);


INSERT INTO LOAN (loan_amount, interest_rate, loan_term, monthly_payment, status, customer_id, vehicle_id) VALUES
(20000,5.5,60,380,'approved',1,1),
(25000,6.0,72,420,'approved',2,2),
(30000,4.5,60,560,'pending',3,3),
(45000,5.0,84,650,'approved',4,4),
(55000,6.5,72,900,'rejected',5,5),
(40000,5.8,60,770,'approved',6,6),
(18000,4.0,48,400,'approved',7,7),
(22000,5.2,60,430,'pending',8,8),
(28000,6.1,72,500,'approved',9,9),
(26000,5.9,60,480,'approved',10,10);

INSERT INTO LOAN_PAYMENT (payment_date, amount, loan_id) VALUES
('2026-04-01',380,1),
('2026-04-02',340,2),
('2026-04-03',350,3),
('2026-04-04',360,4),
('2026-04-05',400,5),
('2026-04-06',320,6),
('2026-04-07',450,7),
('2026-04-08',480,8),
('2026-04-09',310,9),
('2026-04-10',370,10);

-- Loan payments accounting
INSERT INTO ACCOUNTING_TRANSACTION (transaction_type, amount, transaction_date, department_id, payment_id) VALUES
('Loan Payment',380,'2026-04-01',7,1),
('Loan Payment',340,'2026-04-02',7,2),
('Loan Payment',350,'2026-04-03',7,3),
('Loan Payment',360,'2026-04-04',7,4),
('Loan Payment',400,'2026-04-05',7,5),
('Loan Payment',320,'2026-04-06',7,6),
('Loan Payment',450,'2026-04-07',7,7),
('Loan Payment',480,'2026-04-08',7,8),
('Loan Payment',310,'2026-04-09',7,9),
('Loan Payment',370,'2026-04-10',7,10);

-- Vehicle Sales accounting
INSERT INTO ACCOUNTING_TRANSACTION (transaction_type, amount, transaction_date, department_id, sale_id) VALUES
('Vehicle Sale',24000,'2024-01-01',1,1),
('Vehicle Sale',26000,'2024-01-05',1,2);
