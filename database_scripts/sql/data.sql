
--
--	Insert data for user table
--

INSERT INTO `user` (`username`, `email`, `first_name`, `last_name`, `password`) 
VALUES ('ironman', 'tony@stark.com', 'Tony', 'Stark', '$2b$12$mbF88pyhx7GfFVocX3gBO.uLn.fU1t9BZBhFPDHpSGSP6aZcSoJk.');

INSERT INTO `user` (`username`, `email`, `first_name`, `last_name`, `password`) 
VALUES ('test', 'test@example.com', 'Sherlock', 'Holmes', '$2b$12$GlQ4DlEKy8AfjmVNa9niLOEi0z3ZtlaXp3rPEqa6tn5tF5QfNlama');

-- -------------------------------------------------------------------------------------------
--
--  Insert data for organisation table
--

INSERT INTO `organisation` (`slug`, `logo`, `name`) 
VALUES ('avengers', 'avengers.jpg', 'Earth Avengers');

INSERT INTO `organisation` (`slug`, `logo`, `name`) 
VALUES ('baker-street', 'VeiwList.png', 'The Gang');

INSERT INTO `organisation` (`slug`, `logo`, `name`) 
VALUES ('e-club', 'avengers.jpg', 'PSG Tech E-Club');

-- -------------------------------------------------------------------------------------------
--
-- Insert data for project table
--

INSERT INTO `project` (`project_id`, `slug`, `name`, `description`, `api_key`) 
VALUES ('flizon', 'e-club', 'flizon', 'Not only do you buy more, but you buy in a broader set of categories.', '85f91771-2c44-41e5-b020');

INSERT INTO `project` (`project_id`, `slug`, `name`, `description`, `api_key`) 
VALUES ('trail', 'avengers', 'Trail App', 'Trail is a lightweight open-source analytics and event logging platform for websites', '7ba0117a3927424b990efc587d7ac8d7');

-- -------------------------------------------------------------------------------------------
--
-- Insert data for belongs_to table
--
INSERT INTO `belongs_to` (`username`, `slug`, `role`) 
VALUES ('test', 'baker-street', 'Admin');

INSERT INTO `belongs_to` (`username`, `slug`, `role`) 
VALUES ('test', 'e-club', 'Admin');

INSERT INTO `belongs_to` (`username`, `slug`, `role`) 
VALUES ('ironman', 'avengers', 'Admin');

INSERT INTO `belongs_to` (`username`, `slug`, `role`) 
VALUES ('ironman', 'e-club', 'Member');