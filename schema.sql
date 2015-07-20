drop table if exists entries;
create table entries (
  key integer primary key,
  url text not null,
  views integer not null
);
