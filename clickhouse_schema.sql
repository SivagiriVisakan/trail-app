CREATE TABLE `web_events` (
  `session_id` UInt64 NOT NULL,
  `time_entered` DateTime NOT NULL,
  `user_agent` String NOT NULL,
  `page_url` String,
  `page_domain` String,
  `page_params` String,
  `event_type` FixedString(50) NOT NULL,
  `custom_data` String NOT NULL
) ENGINE=MergeTree() ORDER BY (page_domain, page_url);


-- To insert an event
-- INSERT into web_events (session_id, time_entered, user_agent, page_url, page_domain, page_params, event_type, custom_data) VALUES (1, now() , 'user_agent', '/home', 'example.com', '{}', 'pageview', '{}');
