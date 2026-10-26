USE company;

INSERT INTO DEPARTMENT (Dnumber, Dname, mgr_ssn, mgr_start_date) VALUES
(1, 'Research', NULL, '2020-01-01'),
(2, 'Administration', NULL, '2021-03-15'),
(3, 'Headquarters', NULL, '2019-06-01');

INSERT INTO EMPLOYEE (ssn, fname, lname, bdate, address, gender, salary, Dno) VALUES
(101, 'mohsen', 'mahmoud', '1985-01-01', '123 Main St, Alexandria', 'M', 50000.00, 1),
(102, 'omar', 'osama', '2006-03-11', '678 louran street, Cairo', 'F', 60000.00, 2),
(103, 'Omar', 'Nassret', '2004-01-01', '789 Elm St, Alexandria', 'M', 75000.00, 3);

UPDATE DEPARTMENT SET mgr_ssn = 101 WHERE Dnumber = 1;
UPDATE DEPARTMENT SET mgr_ssn = 102 WHERE Dnumber = 2;
UPDATE DEPARTMENT SET mgr_ssn = 103 WHERE Dnumber = 3;

INSERT INTO PROJECT (Pnumber, Pname, Plocation, Dno) VALUES
(10, 'Project Alpha', 'Alexandria', 1),
(20, 'Project Beta', 'Cairo', 2),
(30, 'Project Gamma', 'Giza', 3);