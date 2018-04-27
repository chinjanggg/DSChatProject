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

