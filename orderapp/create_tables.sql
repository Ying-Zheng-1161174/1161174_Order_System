DROP DATABASE IF EXISTS orderapp;
CREATE DATABASE orderapp;
USE orderapp;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        firstname VARCHAR(100) NOT NULL, 
        lastname VARCHAR(100) NOT NULL, 
        username VARCHAR(50) NOT NULL, 
        password_hash VARCHAR(255) NOT NULL, 
        type VARCHAR(50), 
        PRIMARY KEY (id), 
        UNIQUE (username)
);

DROP TABLE IF EXISTS staffs;
CREATE TABLE staffs (
        id INTEGER NOT NULL, 
        `dateJoined` DATE NOT NULL, 
        `deptName` VARCHAR(100) NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES users (id)
);

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
        id INTEGER NOT NULL, 
        `custAddress` VARCHAR(255) NOT NULL, 
        `custBalance` FLOAT NOT NULL, 
        `maxOwing` FLOAT NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES users (id)
);

DROP TABLE IF EXISTS corporate_customers;
CREATE TABLE corporate_customers (
        id INTEGER NOT NULL, 
        `discountRate` FLOAT NOT NULL, 
        `maxCredit` FLOAT NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES customers (id)
);

DROP TABLE IF EXISTS items;
CREATE TABLE items (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        type VARCHAR(50), 
        stock INTEGER, 
        PRIMARY KEY (id)
);

DROP TABLE IF EXISTS veggies;
CREATE TABLE veggies (
        id INTEGER NOT NULL, 
        `vegName` VARCHAR(100) NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES items (id)
);

DROP TABLE IF EXISTS weighted_veggies;
CREATE TABLE weighted_veggies (
        id INTEGER NOT NULL, 
        weight FLOAT NOT NULL, 
        `weightPerKilo` FLOAT NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES veggies (id)
);

DROP TABLE IF EXISTS pack_veggies;
CREATE TABLE pack_veggies (
        id INTEGER NOT NULL, 
        `numOfPack` INTEGER NOT NULL, 
        `pricePerPack` FLOAT NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES veggies (id)
);

DROP TABLE IF EXISTS unit_price_veggies;
CREATE TABLE unit_price_veggies (
        id INTEGER NOT NULL, 
        quantity INTEGER NOT NULL, 
        `pricePerUnit` FLOAT NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES veggies (id)
);

DROP TABLE IF EXISTS premade_boxes;
CREATE TABLE premade_boxes (
        id INTEGER NOT NULL, 
        `boxSize` ENUM('Small','Medium','Large') NOT NULL, 
        `numOfBoxes` INTEGER NOT NULL, 
        price FLOAT NOT NULL, 
        `isCustom` BOOL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES items (id)
);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        `orderDate` DATE NOT NULL, 
        `orderNumber` VARCHAR(50) NOT NULL, 
        `deliveryMethod` ENUM('Delivery','Pickup') NOT NULL, 
        `orderStatus` ENUM('Pending','Processed','Completed','Cancelled') NOT NULL, 
        `paymentMethod` ENUM('Credit Card','Debit Card','Account') NOT NULL, 
        customer_id INTEGER NOT NULL, 
        PRIMARY KEY (id), 
        UNIQUE (`orderNumber`), 
        FOREIGN KEY(customer_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS order_lines;
CREATE TABLE order_lines (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        order_id INTEGER, 
        item_id INTEGER, 
        quantity FLOAT NOT NULL, 
        subtotal FLOAT NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(order_id) REFERENCES orders (id), 
        FOREIGN KEY(item_id) REFERENCES items (id)
);

DROP TABLE IF EXISTS payments;
CREATE TABLE payments (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        `paymentAmount` FLOAT NOT NULL, 
        `paymentDate` DATE NOT NULL, 
        type VARCHAR(50), 
        customer_id INTEGER NOT NULL, 
        order_id INTEGER NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(customer_id) REFERENCES customers (id), 
        UNIQUE (order_id), 
        FOREIGN KEY(order_id) REFERENCES orders (id)
);

DROP TABLE IF EXISTS credit_card_payments;
CREATE TABLE credit_card_payments (
        id INTEGER NOT NULL, 
        `cardExpiryDate` DATE NOT NULL, 
        `cardNumber` VARCHAR(16) NOT NULL, 
        `cardType` VARCHAR(50) NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES payments (id)
);

DROP TABLE IF EXISTS debit_card_payments;
CREATE TABLE debit_card_payments (
        id INTEGER NOT NULL, 
        `bankName` VARCHAR(100) NOT NULL, 
        `debitCardNumber` VARCHAR(16) NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES payments (id)
);

DROP TABLE IF EXISTS account_payments;
CREATE TABLE account_payments (
        id INTEGER NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(id) REFERENCES payments (id)
);

DROP TABLE IF EXISTS box_contents;
CREATE TABLE box_contents (
        box_id INTEGER, 
        veggie_id INTEGER, 
        customer_id INTEGER, 
        order_id INTEGER, 
        FOREIGN KEY(box_id) REFERENCES premade_boxes (id), 
        FOREIGN KEY(veggie_id) REFERENCES veggies (id), 
        FOREIGN KEY(customer_id) REFERENCES customers (id), 
        FOREIGN KEY(order_id) REFERENCES orders (id)
);