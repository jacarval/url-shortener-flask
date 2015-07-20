drop table if exists entries;
create table entries (
  key text primary key,
  url text not null,
  views integer not null
);
