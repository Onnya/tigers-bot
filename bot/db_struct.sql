-- auto-generated definition
create table users
(
    id          integer
        primary key autoincrement,
    telegram_id integer not null,
    photo       text,
    step        text
);

