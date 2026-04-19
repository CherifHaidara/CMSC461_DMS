CREATE DATABASE IF NOT EXISTS car_dealership;
USE car_dealership;

CREATE TABLE DIVISION (
    division_id   INT PRIMARY KEY AUTO_INCREMENT,
    division_name VARCHAR(100) NOT NULL,
    description   VARCHAR(255)
);

CREATE TABLE DEPARTMENT (
    department_id   INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL,
    description     VARCHAR(255),
    status          VARCHAR(50),
    division_id     INT NOT NULL,
    FOREIGN KEY (division_id) REFERENCES DIVISION(division_id)
);

CREATE TABLE ROLE (
    role_id   INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE EMPLOYEE (
    employee_id   INT PRIMARY KEY AUTO_INCREMENT,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    emp_email     VARCHAR(100),
    emp_phone     VARCHAR(20),
    hire_date     DATE,
    salary        DECIMAL(10, 2),
    position      VARCHAR(100),
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES DEPARTMENT(department_id)
);

CREATE TABLE USER (
    user_id     INT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    employee_id INT NOT NULL,
    role_id     INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    FOREIGN KEY (role_id) REFERENCES ROLE(role_id)
);

CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(50) NOT NULL,
    customer_address VARCHAR(255) NOT NULL,
    customer_email VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE PhoneNumber (
    phone_id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(15) NOT NULL,
    customer_id INT NOT NULL,
    
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_make VARCHAR(50) NOT NULL,
    vehicle_model VARCHAR(50) NOT NULL,
    vehicle_year INT NOT NULL,
    vehicle_vin VARCHAR(50) UNIQUE NOT NULL,
    vehicle_price DECIMAL(10,2) NOT NULL,
    vehicle_mileage INT NOT NULL,
    vehicle_condition ENUM('new', 'used') NOT NULL,
    vehicle_availability_status ENUM('available', 'sold', 'maintenance') NOT NULL,

    CONSTRAINT vehicle_year_chk CHECK (vehicle_year >= 1900),
    CONSTRAINT vehicle_price_chk CHECK (vehicle_price >= 0),
    CONSTRAINT vehicle_mileage_chk CHECK (vehicle_mileage >= 0)
);

CREATE TABLE Sale (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_date DATE NOT NULL,
    sale_price DECIMAL(10,2) NOT NULL,
    financing_option ENUM('cash', 'loan', 'lease') NOT NULL,
    payment_method ENUM('credit_card', 'debit_card', 'cash', 'bank_transfer') NOT NULL,
    vehicle_id INT NOT NULL,
    customer_id INT NOT NULL,
    department_id INT NOT NULL,
    employee_id INT NOT NULL,

    CONSTRAINT sale_price_chk CHECK (sale_price >= 0),

    CONSTRAINT fk_sale_vehicle FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    CONSTRAINT fk_sale_customer FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    CONSTRAINT fk_sale_department FOREIGN KEY (department_id) REFERENCES Department(department_id),
    CONSTRAINT fk_sale_employee FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);