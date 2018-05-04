/*
getUnread เอาเฉพาะข้อความหลัง break (cancelBreak แล้วจะไม่มีข้อความ)
getmessage เรียกข้อความก่อน break ไม่เอาข้อความหลัง break (ถ้าไม่ break จะเรียกทุกข้อความ)
breakGroup จะ break แล้วจำว่า break ที่ข้อความไหน

*/





DROP PROCEDURE IF EXISTS `createUser`;
DELIMITER &&
CREATE DEFINER=`root`@`localhost` PROCEDURE `createUser`(IN iCID VarChar(20), IN iName VARCHAR(255), IN iPass VARCHAR(255))
BEGIN	INSERT INTO client( 
		CID,
		DisplayName,
		Password) 
      VALUE(
		iCID,
		iName,
		iPass);
END&&
DELIMITER ;

DROP function IF EXISTS `getTime`;
DELIMITER &&
CREATE DEFINER=`root`@`localhost` FUNCTION `getTime`() RETURNS datetime
BEGIN
	RETURN now();
END&&
DELIMITER ;

DROP PROCEDURE IF EXISTS storeMessage;
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

DROP function IF EXISTS `getLastMID`;
DELIMITER &&
CREATE DEFINER=`root`@`localhost` FUNCTION `getLastMID`() RETURNS INT
BEGIN
	DECLARE LM INT;
	SELECT MAX(MID) FROM message INTO LM;
    IF LM is NULL THEN SET LM = 0;
    END IF;
	RETURN LM;
END&&
DELIMITER ;

DROP PROCEDURE IF EXISTS breakGroup;
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

DROP PROCEDURE IF EXISTS cancelBreak;
DELIMITER //
CREATE PROCEDURE cancelBreak (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	delete from break where CID=iCID and GID= iGID;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS joinGroup;
DELIMITER //
CREATE PROCEDURE joinGroup (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	INSERT INTO clientingroup(  
		  CID,
		  GID,
          StartMID
          ) 
      VALUE(
		iCID,
		iGID,
        getLastMID());
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS leaveGroup;
DELIMITER //
CREATE PROCEDURE leaveGroup (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	DELETE FROM clientingroup WHERE CID=iCID and GID=iGID; 
    END //
DELIMITER ;

DROP PROCEDURE IF EXISTS createGroup;
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

DROP PROCEDURE IF EXISTS getUnread;
DELIMITER //
CREATE PROCEDURE getUnread (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	SELECT * FROM message M WHERE M.GID = iGID and M.MID > 
    (select b.MID from break b where b.CID = iCID and b.GID = iGID);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getMessage;
DELIMITER //
CREATE PROCEDURE getMessage (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN

		IF (SELECT EXISTS(SELECT * FROM break b WHERE b.CID=iCID and b.GID=iGID))
		THEN 	SELECT M.MID, M.Timestamp, M.Text, M.GID, M.CID 
				FROM message M, break b 
                WHERE M.GID = iGID and b.MID >= M.MID and M.MID > 
				(SELECT cig.StartMID FROM clientingroup cig where cig.GID=iGID and cig.CID=iCID);
        
        ELSE SELECT M.MID, M.Timestamp, M.Text, M.GID, M.CID 
			FROM message M
			WHERE M.GID = iGID and M.MID > 
            (SELECT cig.StartMID FROM clientingroup cig where cig.GID=iGID and cig.CID=iCID);
	
        END IF;
END //
DELIMITER ;