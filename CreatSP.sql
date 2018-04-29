DELIMITER &&
CREATE DEFINER=`root`@`localhost` PROCEDURE `createUser`(IN iName VARCHAR(255), IN iPass VARCHAR(255))
BEGIN
	INSERT INTO client(  
		  DisplayName,
          Password) 
      VALUE(
		iName,
		iPass);
END&&
DELIMITER ;

DELIMITER &&
CREATE DEFINER=`root`@`localhost` FUNCTION `getTime`() RETURNS datetime
BEGIN
	RETURN now();
END&&
DELIMITER ;

DELIMITER //
CREATE PROCEDURE storeMessage (IN iCID VarChar(20), IN iGID VarChar(20), IN iText VARCHAR(255))
BEGIN
	
	INSERT INTO message(  
		  Timestamp,
		  Text,
		  CID,
		  GID) 
      VALUE(
		getTime(),
		iText,
		iCID,
		iGID);
END //
DELIMITER ;

DELIMITER &&
CREATE DEFINER=`root`@`localhost` FUNCTION `getLastMID`() RETURNS INT
BEGIN
	DECLARE LM INT;
	SELECT MAX(MID) FROM message INTO LM;
	RETURN LM;
END&&
DELIMITER ;


DELIMITER //
CREATE PROCEDURE breakGroup (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	
	INSERT INTO break(  
		  CID,
		  GID,
          MID) 
      VALUE(
		iCID,
		iGID,
        getLastMID());
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE cancelBreak (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	delete from break where CID=iCID and GID= iGID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE joinGroup (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	INSERT INTO clientingroup(  
		  CID,
		  GID
          ) 
      VALUE(
		iCID,
		iGID);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE createGroup (IN iGID VarChar(20), IN iName VarChar(255))
BEGIN
	INSERT INTO cgroup(  
		  GID,
          GName
          ) 
      VALUE(
		iGID,
        iName);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE getUnread (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	SELECT * FROM message M WHERE M.GID = iGID and M.MID > 
    (select b.MID from break b where b.CID = iCID and b.GID = iGID);
END //
DELIMITER ;


/* test
call createUser('00000000000000000001', 'a','1');
call createUser('00000000000000000002', 'b','2');

call createGroup('00000000000000000001', 'CG1');

call joinGroup('00000000000000000001','00000000000000000001');
call joinGroup('00000000000000000002','00000000000000000001');

call createGroup('00000000000000000002', 'b');
call storeMessage('00000000000000000001','00000000000000000001','a test1');
call storeMessage('00000000000000000002','00000000000000000001','b test2');

call breakGroup('00000000000000000001','00000000000000000001');

call storeMessage('00000000000000000002','00000000000000000001','b test3');
call storeMessage('00000000000000000002','00000000000000000001','b test4');
call getUnread('00000000000000000001', '00000000000000000001');


call cancelBreak('00000000000000000001','00000000000000000001');
*/
