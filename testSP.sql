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