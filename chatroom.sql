DROP DATABASE IF EXISTS chatroom;
CREATE DATABASE chatroom;

\c chatroom;

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
-- --------------------------------------------------------



CREATE TABLE IF NOT EXISTS userlist (
  id serial,
  username varchar(30),
  password varchar(150),
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS names(
    id serial,
    tableName varchar(20) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS NSA (
    id serial,
    username varchar(30) NOT NULL,
    message varchar(500) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS Chats (
    id serial, 
    room varchar(30),
    user_in_room varchar(30),
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS Spammers(
    id SERIAL ,
    username varchar(30) NOT NULL,
    message varchar(500) NOT NULL,
    PRIMARY KEY(id)
);
CREATE TABLE IF NOT EXISTS Police(
    id SERIAL NOT NULL,
    username varchar(30) NOT NULL,
    message varchar(500) NOT NULL,
    PRIMARY KEY(id)
);

INSERT INTO userlist (username,password) VALUES ('falbellaihi',crypt('fhfh', gen_salt('bf')));
INSERT INTO userlist (username,password) VALUES ('user',crypt('test', gen_salt('bf')));
INSERT INTO Chats (room, user_in_room) VALUES('NSA','user');
INSERT INTO NSA (username,message) VALUES ('user','testing system idea');
INSERT INTO names(tableName) VALUES('NSA');
INSERT INTO names(tableName) VALUES('Police');
INSERT INTO names(tableName) VALUES('Spammers');
