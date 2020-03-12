SET feed off
SET head off
SET pagesize 0
SET line 2000
SELECT '{' || listagg(param_from_db,', ') WITHIN GROUP (ORDER BY param_from_db) || '}'
FROM (
    (SELECT '"' || a.tablespace_name || '":{"free":' || free || ',"total":' || total || '}' param_from_db FROM
        (SELECT tablespace_name, round(SUM(bytes)/1024/1024) AS total FROM dba_data_files GROUP BY tablespace_name) a,
        (SELECT tablespace_name, round(SUM(bytes)/1024/1024) AS free FROM dba_free_space GROUP BY tablespace_name) b
    WHERE a.tablespace_name = b.tablespace_name)
    UNION
    (SELECT '"' || a.tablespace_name || '":{"free":' || (total - used_mbytes) || ',"total":' || total || '}' param_from_db FROM
        (SELECT tablespace_name, round(SUM(bytes_used + bytes_free)/1024/1024) AS total FROM v$temp_space_header GROUP BY tablespace_name) a,
        (SELECT tablespace_name, round(used_blocks*8/1024) AS used_mbytes FROM v$sort_segment) b
    WHERE a.tablespace_name = b.tablespace_name)
);
EXIT;
