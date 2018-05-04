CREATE USER 'ds_chat'@'localhost' IDENTIFIED BY 'alchemy';
REVOKE ALL PRIVILEGES, grant option from 'ds_chat'@'localhost';
GRANT ALL PRIVILEGES ON ds_chat.* TO 'ds_chat'@'localhost';

CREATE SCHEMA `ds_chat` ;

use ds_chat;

CREATE TABLE Client
(
  CID VARCHAR(20) NOT NULL,
  DisplayName VARCHAR(255) NOT NULL,
  Password VARCHAR(255) NOT NULL,
  PRIMARY KEY (CID)
);

CREATE TABLE CGroup
(
  GID VARCHAR(20) NOT NULL,
  GName VARCHAR(255),
  PRIMARY KEY (GID)
);

CREATE TABLE ClientInGroup
(
  CID VARCHAR(20) NOT NULL,
  GID VARCHAR(20) NOT NULL,
  PRIMARY KEY (CID, GID),
  FOREIGN KEY (CID) REFERENCES Client(CID),
  FOREIGN KEY (GID) REFERENCES CGroup(GID)
);

CREATE TABLE Message
(
  MID int NOT NULL auto_increment,
  Timestamp datetime,
  Text VARCHAR(255),
  CID VARCHAR(20) NOT NULL,
  GID VARCHAR(20) NOT NULL,
  PRIMARY KEY (MID),
  FOREIGN KEY (CID) REFERENCES Client(CID),
  FOREIGN KEY (GID) REFERENCES CGroup(GID)
);

CREATE TABLE Break
(
  CID VARCHAR(20) NOT NULL,
  GID VARCHAR(20) NOT NULL,
  MID int NOT NULL,
  PRIMARY KEY (CID, GID),
  FOREIGN KEY (CID) REFERENCES Client(CID),
  FOREIGN KEY (GID) REFERENCES CGroup(GID),
  FOREIGN KEY (MID) REFERENCES Message(MID)
);

