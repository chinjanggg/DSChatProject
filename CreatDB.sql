/*
CREATE USER 'ds_chat'@'localhost' IDENTIFIED BY 'alchemy';
REVOKE ALL PRIVILEGES, grant option from 'ds_chat'@'localhost';
GRANT ALL PRIVILEGES ON ds_chat.* TO 'ds_chat'@'localhost';
*/

use ds_chat;
SET foreign_key_checks = 0;
DROP TABLE IF EXISTS client;
CREATE TABLE Client
(
  CID VARCHAR(20) NOT NULL,
  DisplayName VARCHAR(255) NOT NULL,
  Password VARCHAR(255) NOT NULL,
  PRIMARY KEY (CID)
);

DROP TABLE IF EXISTS cgroup;
CREATE TABLE CGroup
(
  GID VARCHAR(20) NOT NULL,
  GName VARCHAR(255),
  PRIMARY KEY (GID)
);

DROP TABLE IF EXISTS clientingroup;
CREATE TABLE ClientInGroup
(
  CID VARCHAR(20) NOT NULL,
  GID VARCHAR(20) NOT NULL,
  StartMID INT NOT NULL,
  PRIMARY KEY (CID, GID),
  FOREIGN KEY (CID) REFERENCES Client(CID),
  FOREIGN KEY (GID) REFERENCES CGroup(GID)
);

DROP TABLE IF EXISTS message;
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

DROP TABLE IF EXISTS break;
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
SET foreign_key_checks = 1;

call createUser('admin','admin','admin');
call createGroup('admin', 'admin');
call joinGroup('admin', 'admin');
call storeMessage('admin', 'admin','initialzed');