CREATE TABLE `web_events` (
  `session_id` UInt64 NOT NULL,
  `project_id` 
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
  `custom_data` NESTED 
  (
    `key` String
    `value` String
  )
) ENGINE=MergeTree() ORDER BY (page_domain, time_entered, session_id);
