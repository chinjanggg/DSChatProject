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
		  GID,
          StartMID
          ) 
      VALUE(
		iCID,
		iGID,
        getLastMID());
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE leaveGroup (IN iCID VarChar(20), IN iGID VarChar(20))
BEGIN
	DELETE FROM clientingroup WHERE CID=iCID and GID=iGID; 
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


#test createuser
call createUser('user1','a','1');
call createUser('user2','b','2');

call createGroup('GID1', 'CG1');

call joinGroup('user1','GID1');
call joinGroup('user2','GID1');

call createGroup('GID2', 'cg2');
call storeMessage('user1','GID1','a test1');
call storeMessage('user2','GID1','b test2');

call getMessage('user1','GID1');
call getMessage('user2','GID1');

# test break
call breakGroup('user1','GID1');

call storeMessage('user2','GID1','b test3');
call storeMessage('user2','GID1','b test4');

# user1 should get 123 user2 get 1234
call getMessage('user1','GID1');
call getMessage('user2','GID1');
#user1 get 4
call getUnread('user1','GID1');

call cancelBreak('user1','GID1');
# now user1 get 1234
call getMessage('user1','GID1');

call leaveGroup('user1','GID1');
