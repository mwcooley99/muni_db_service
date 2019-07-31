-- Delete duplicate values
DELETE
FROM predictions
WHERE ctid IN
      (SELECT ctid
       FROM (SELECT ctid,
                    ROW_NUMBER() OVER
                        (PARTITION BY line_ref, direction_ref, stop_point_ref, scheduled_arrival_time ORDER BY ctid) AS rnum
             FROM predictions) t
       WHERE t.rnum > 1);

SELECT count(*)
FROM predictions;


SELECT *
FROM (
         SELECT ctid
         FROM (
                  SELECT ctid,
                         p.recorded_time,
                         t                      AS local,
                         extract(ISODOW FROM t) AS dow
                  FROM (
                           SELECT *,
                                  (recorded_time AT TIME ZONE
                                   'utc' AT TIME ZONE
                                   'america/los_angeles') AS t
                           FROM predictions
                       ) p
              ) h
         WHERE h.dow IN (6, 7)) g;

-- Delete weekend days
DELETE
FROM predictions
WHERE ctid IN (
    SELECT ctid
    FROM (
             SELECT ctid,
                    recorded_time,
                    recorded_time AT TIME ZONE
                    'utc' AT TIME ZONE
                    'america/los_angeles'                      AS local,
                    extract(ISODOW FROM recorded_time AT TIME ZONE
                                        'utc' AT TIME ZONE
                                        'america/los_angeles') AS dow
             FROM predictions
         ) AS g
    WHERE g.dow IN (6, 7)
);

-- Verify all weekend days are deleted
SELECT *
FROM (
         SELECT ctid,
                recorded_time,
                recorded_time AT TIME ZONE
                'utc' AT TIME ZONE
                'america/los_angeles'                      AS local,
                extract(ISODOW FROM recorded_time AT TIME ZONE
                                    'utc' AT TIME ZONE
                                    'america/los_angeles') AS dow
         FROM predictions
     ) AS g
WHERE g.dow IN (6, 7)