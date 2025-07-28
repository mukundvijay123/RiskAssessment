SELECT
    p.id AS process_id,
    p.name AS process_name,
    p.process_owner,
    p.subdepartment_id,
    bpi.id AS bia_process_info_id,
    bpi.description,
    bpi.critical,
    bpi.review_status,
    bpi.created_at AS bia_created_at,
    bpi.updated_at AS bia_updated_at
FROM
    process p
JOIN
    bia_process_info bpi
    ON p.id = bpi.process_id
WHERE
    bpi.critical = TRUE;
