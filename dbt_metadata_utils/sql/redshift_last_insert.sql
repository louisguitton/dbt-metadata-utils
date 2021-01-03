-- The STL tables only retain approximately two to five days of log history.
-- https://stackoverflow.com/questions/38514599/amazon-redshift-how-to-get-the-last-date-a-table-inserted-data
-- https://docs.aws.amazon.com/redshift/latest/dg/r_STL_INSERT.html
select
    sti.schema,
    sti.table,
    sq.endtime,
    sq.querytxt
from
    (
        select
            max(query) as query,
            tbl,
            max(i.endtime) as last_insert
        from
            stl_insert i
        group by
            tbl
        order by
            tbl
    ) inserts
    join stl_query sq on sq.query = inserts.query
    join svv_table_info sti on sti.table_id = inserts.tbl
order by
    sq.endtime asc;
