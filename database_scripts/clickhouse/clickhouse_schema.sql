CREATE TABLE `web_events` (
  `session_id` FixedString(64) NOT NULL,
  `project_id` String NOT NULL,
  `origin_user_id` String NOT NULL,
  `time_entered` DateTime NOT NULL,
  `user_agent` String NOT NULL,
  `page_url` String,
  `page_domain` String,
  `page_params` String,
  `event_type` FixedString(50) NOT NULL,
  `browser` String,
  `os` String,
  `device` String,
  `referrer` String,
  `utm_campaign` String,
  `custom_data` Nested 
  (
    `key` String,
    `value` String
  )
) ENGINE=MergeTree() ORDER BY (page_domain, time_entered, session_id);


-- Get count of total_visitors between two dates
-- select event_date, sum(total_visitors) from (SELECT toDate(time_entered) as event_date, uniqExact(origin_user_id) as total_visitors FROM web_events WHERE project_id='abcdef' and toDate(time_entered) BETWEEN '2020-11-01' and '2020-11-11' group by  toDate(time_entered), origin_user_id order by origin_user_id) group by event_date


-- Get the count of particular events datewise
-- select toDate(time_entered) as event_date, count(*) as pageviews from web_events where project_id='abcdef' and event_type='pageview' group by event_date


-- Get the count of all the events datewise
-- select toDate(time_entered) as event_date, count(*) as total_events from web_events where project_id='abcdef' group by event_date

-- Get the count of events categorywise, grouped by date
-- select toDate(time_entered) as event_date, event_type, count(*) as total_events from web_events where project_id='abcdef' group by event_date, event_type


-- select toDate(time_entered) as event_date, os, count(*) from (select distinct(session_id), os, time_entered from web_events order by time_entered) group by event_date,os

-- select page_url, session_id as start_page from web_events where (session_id, time_entered) in ((select session_id, min(time_entered) from web_events group by session_id) where page_url, session_id in (select page_url, session_id as end_page from web_events where (session_id, time_entered) in (select session_id, max(time_entered) from web_events group by session_id)))

