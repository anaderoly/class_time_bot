create or replace function get_class_times(
    p_user_id   bigint,
    p_start_dt  date,
    p_stop_dt   date
)
returns table (
    class_name   text,
    total_time_h numeric
)
language sql
as $$
with latest as (
    select
        user_id,
        work_date,
        max(created_at) as created_at
    from lessons
    where user_id = p_user_id
      and work_date between p_start_dt and p_stop_dt
    group by user_id, work_date
)
select
    l.class_name,
    sum(l.class_time_h) as class_time_h
from lessons l
join latest using (user_id, work_date, created_at)
group by l.class_name
order by l.class_name;
$$;
