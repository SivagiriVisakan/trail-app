CREATE TABLE `user` (
  `username` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


ALTER TABLE `user`
  ADD PRIMARY KEY (`username`);
COMMIT;


CREATE TABLE `workspace` (
  `slug` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE `workspace`
  ADD PRIMARY KEY (`slug`);
COMMIT;

CREATE TABLE `project` (
  `project_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE `project`
  ADD PRIMARY KEY (`project_id`),
  ADD KEY `slug` (`slug`);


ALTER TABLE `project`
  ADD CONSTRAINT `project_ibfk_1` FOREIGN KEY (`slug`) REFERENCES `workspace` (`slug`) ON DELETE RESTRICT ON UPDATE RESTRICT;
COMMIT;

CREATE TABLE `event` (
  `event_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `origin_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_type` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `custom_data` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


ALTER TABLE `event`
  ADD PRIMARY KEY (`event_id`),
  ADD KEY `project_id` (`project_id`);


ALTER TABLE `event`
  ADD CONSTRAINT `event_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
COMMIT;

CREATE TABLE `belongs_to` (
  `username` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


ALTER TABLE `belongs_to`
  ADD PRIMARY KEY (`username`,`slug`),
  ADD KEY `slug` (`slug`);

ALTER TABLE `belongs_to`
  ADD CONSTRAINT `belongs_to_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `belongs_to_ibfk_2` FOREIGN KEY (`slug`) REFERENCES `workspace` (`slug`) ON DELETE RESTRICT ON UPDATE RESTRICT;
COMMIT;

CREATE TABLE `permission` (
  `username` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE `permission`
  ADD PRIMARY KEY (`username`,`project_id`),
  ADD KEY `project_id` (`project_id`);

ALTER TABLE `permission`
  ADD CONSTRAINT `permission_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `permission_ibfk_2` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT;
COMMIT;






























