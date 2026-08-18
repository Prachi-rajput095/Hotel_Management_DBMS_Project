CREATE DATABASE IF NOT EXISTS hotel_management;
USE hotel_management;

DROP TRIGGER IF EXISTS after_booking_insert;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS service_usage;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(255)
);

CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    room_type ENUM('Single','Double','Deluxe','Suite') NOT NULL,
    price_per_night DECIMAL(10,2) NOT NULL,
    status ENUM('Available','Booked','Maintenance') DEFAULT 'Available'
);

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status ENUM('Confirmed','Checked-In','Checked-Out','Cancelled') DEFAULT 'Confirmed',
    CONSTRAINT fk_booking_customer FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_booking_room FOREIGN KEY (room_id)
        REFERENCES rooms(room_id) ON DELETE RESTRICT
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('Cash','Card','UPI') NOT NULL,
    CONSTRAINT fk_payment_booking FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id) ON DELETE CASCADE
);

CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE service_usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    service_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    usage_date DATE NOT NULL,
    CONSTRAINT fk_usage_booking FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id) ON DELETE CASCADE,
    CONSTRAINT fk_usage_service FOREIGN KEY (service_id)
        REFERENCES services(service_id) ON DELETE RESTRICT
);

DELIMITER //

CREATE TRIGGER after_booking_insert
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    UPDATE rooms
    SET status = 'Booked'
    WHERE room_id = NEW.room_id;
END//

DELIMITER ;

INSERT INTO customers (customer_name, phone, email, address) VALUES
('Rahul Sharma','9876543210','rahul@gmail.com','Delhi'),
('Priya Patel','9876543211','priya@gmail.com','Ahmedabad'),
('Amit Kumar','9876543212','amit@gmail.com','Mumbai'),
('Neha Singh','9876543213','neha@gmail.com','Jaipur'),
('Arjun Verma','9876543214','arjun@gmail.com','Pune');

INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES
('101','Single',1500,'Available'),
('102','Single',1500,'Available'),
('201','Double',2500,'Available'),
('202','Double',2500,'Available'),
('301','Deluxe',4000,'Available'),
('302','Deluxe',4000,'Available'),
('401','Suite',6500,'Available');

INSERT INTO services (service_name, price) VALUES
('Room Service',500),
('Laundry',300),
('Breakfast',250),
('Airport Pickup',1000);

INSERT INTO bookings (customer_id, room_id, check_in, check_out, status) VALUES
(1,1,'2026-08-20','2026-08-22','Confirmed'),
(2,5,'2026-08-21','2026-08-24','Confirmed'),
(3,7,'2026-08-22','2026-08-25','Confirmed');

INSERT INTO payments (booking_id, amount, payment_method) VALUES
(1,3000,'UPI'),
(2,12000,'Card'),
(3,19500,'Cash');

INSERT INTO service_usage (booking_id, service_id, quantity, usage_date) VALUES
(1,1,1,'2026-08-20'),
(2,3,2,'2026-08-22'),
(3,4,1,'2026-08-22');
