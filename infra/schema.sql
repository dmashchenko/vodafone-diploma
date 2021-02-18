CREATE SCHEMA IF NOT EXISTS base_station;

USE base_station;

CREATE TABLE IF NOT EXISTS traffic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    traffic_prediction FLOAT,
    traffic_real FLOAT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)