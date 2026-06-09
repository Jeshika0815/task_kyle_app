CREATE DATABASE `task_agent_db`;
USE `task_agent_db`;
CREATE TABLE test_data(id INT PRIMARY KEY AUTO_INCREMENT, title VARCHAR(30) NOT NULL);

INSERT INTO test_data(title) VALUES('testdata1');
