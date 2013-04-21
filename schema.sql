create table user (
  user_id integer primary key autoincrement,
  username string not null,
  pw_hash string not null,
  email string not null,
  score integer not null
);

create table task (
  task_id integer primary key autoincrement,
  title string not null,
  description string not null,
  value integer not null
);

create table approval (
  approval_id integer primary key autoincrement,
  entry integer not null,
  sender integer not null,
  FOREIGN KEY(entry) REFERENCES entry(entry_id),
  FOREIGN KEY(sender) REFERENCES user(user_id)	
)

create table entry (
  entry_id integer primary key autoincrement,
  sender integer not null,
  receiver integer not null,
  task integer not null,
  datetime string not null,
  proof string,
  approval integer,
  FOREIGN KEY(sender) REFERENCES user(user_id)
  FOREIGN KEY(receiver) REFERENCES user(user_id)
  FOREIGN KEY(task) REFERENCES task(task_id)
);