
--
-- Table structure for table `belongs_to`
--

CREATE TABLE `belongs_to` (
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(10) COLLATE utf8_unicode_ci DEFAULT 'Member'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `organisation`
--

CREATE TABLE `organisation` (
  `slug` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `permission`
--

CREATE TABLE `permission` (
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `project`
--

CREATE TABLE `project` (
  `project_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `session`
--

CREATE TABLE `session` (
  `session_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `origin_id` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `project_id` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `start_page` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `end_page` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `web_event`
--

CREATE TABLE `web_event` (
  `event_id` bigint(20) NOT NULL,
  `session_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `time_entered` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_agent` varchar(250) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `page_url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `event_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `custom_data` json NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `belongs_to`
--
ALTER TABLE `belongs_to`
  ADD PRIMARY KEY (`username`,`slug`),
  ADD KEY `slug` (`slug`);

--
-- Indexes for table `organisation`
--
ALTER TABLE `organisation`
  ADD PRIMARY KEY (`slug`);

--
-- Indexes for table `permission`
--
ALTER TABLE `permission`
  ADD PRIMARY KEY (`username`,`project_id`),
  ADD KEY `project_id` (`project_id`);

--
-- Indexes for table `project`
--
ALTER TABLE `project`
  ADD PRIMARY KEY (`project_id`),
  ADD KEY `slug` (`slug`);

--
-- Indexes for table `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`session_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`username`);

--
-- Indexes for table `web_event`
--
ALTER TABLE `web_event`
  ADD PRIMARY KEY (`event_id`),
  ADD KEY `web_event_ibfk_1` (`session_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `web_event`
--
ALTER TABLE `web_event`
  MODIFY `event_id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `belongs_to`
--
ALTER TABLE `belongs_to`
  ADD CONSTRAINT `belongs_to_ibfk_2` FOREIGN KEY (`slug`) REFERENCES `organisation` (`slug`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `belongs_to_ibfk_3` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `permission`
--
ALTER TABLE `permission`
  ADD CONSTRAINT `permission_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `permission_ibfk_2` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `project`
--
ALTER TABLE `project`
  ADD CONSTRAINT `project_ibfk_1` FOREIGN KEY (`slug`) REFERENCES `organisation` (`slug`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `web_event`
--
ALTER TABLE `web_event`
  ADD CONSTRAINT `web_event_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `session` (`session_id`) ON DELETE CASCADE ON UPDATE RESTRICT;
COMMIT;
