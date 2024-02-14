drop database chat_db;
create database chat_db;
use chat_db;

create table users (
	id int auto_increment,
    name varchar(50) not null,
    password varchar(255) not null,
    primary key (id)
);

create table messages (
	id int auto_increment,
    sender_id int not null,
    receiver_id int not null,
    message text not null,
    primary key (id),
    foreign key (sender_id) references users(id),
    foreign key (receiver_id) references users(id)
);

create table sessions (
	id int auto_increment,
    user_id int not null,
    primary key (id),
    foreign key (user_id) references users(id)    
);

delete from users;
delete from sessions;
select * from users;
select * from sessions;
select * from messages;
SELECT users.id, users.name FROM users JOIN sessions ON users.id = sessions.user_id;