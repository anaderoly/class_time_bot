create or replace function public.get_class_names(
    p_user_id bigint,
    p_exclude_dates date[]
)
returns table(class_name text) as $$
begin
    return query
    with latest as (
        select user_id, work_date, max(created_at) as created_at
        from lessons
        where user_id = p_user_id
          and (p_exclude_dates is null or work_date not in (select unnest(p_exclude_dates)))
        group by user_id, work_date
    )
    select distinct l.class_name
    from lessons l
    join latest lt on l.user_id = lt.user_id
        and l.work_date = lt.work_date
        and l.created_at = lt.created_at;
end;
$$ language plpgsql;
