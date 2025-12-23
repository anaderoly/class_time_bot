create table lessons (
  user_id bigint not null,
  created_at timestamptz not null default now(),
  work_date date not null,
  work_time_h int not null,
  lesson_num int not null,
  class_name text not null,
  class_time_h float not null
)