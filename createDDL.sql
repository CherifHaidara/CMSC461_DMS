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

CREATE TABLE `USER` (
    user_id     INT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    employee_id INT NOT NULL,
    role_id     INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    FOREIGN KEY (role_id) REFERENCES ROLE(role_id)
);
