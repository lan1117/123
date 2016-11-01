CREATE DATABASE photoshare;
USE photoshare;

/*SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Albums_own;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Users;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Pictures_Album;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Tag;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Comments_photo;
SET FOREIGN_KEY_CHECKS=1;

DROP TABLE Picture_tags CASCADE;
DROP TABLE users_leave_comment CASCADE;
DROP TABLE friends CASCADE;*/

CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    fname varchar(255),
    lname varchar(255),
    email varchar(255) UNIQUE,
    dob varchar(255),
    hometown varchar(255),
    gender varchar(255),
    password varchar(255),
    PRIMARY KEY (user_id)
);

CREATE TABLE Albums_own (
  album_id int4 AUTO_INCREMENT,
  alname varchar(255),
  docreation varchar(255),
  user_id int4 NOT NULL,
  PRIMARY KEY (album_id),
  FOREIGN KEY (user_id)
      REFERENCES Users(user_id)
);

CREATE TABLE Pictures_Album
(
  picture_id int4 AUTO_INCREMENT,
  imgdata longblob ,
  caption varchar(255),
  album_id int NOT NULL,
  PRIMARY KEY (picture_id),
  FOREIGN KEY (album_id)
      REFERENCES Albums_own(album_id)
);

CREATE TABLE Tag(
  tag_id int4 AUTO_INCREMENT,
  tag varchar(255),
  PRIMARY KEY(tag_id)
);

CREATE TABLE Comments_photo(
  comment_id int4 AUTO_INCREMENT,
  cotext varchar(255),
  dohave varchar(255),
  user_id int4,
  picture_id int NOT NULL,
  PRIMARY KEY (comment_id),
  FOREIGN KEY (picture_id)
      REFERENCES Pictures_Album(picture_id)
);

CREATE TABLE Picture_tags(
  user_id int4,
  picture_id int4 AUTO_INCREMENT,
  tag_id int4,
  imgdata longblob ,
  PRIMARY KEY (picture_id, tag_id),
  FOREIGN KEY (picture_id)
      REFERENCES Pictures_Album(picture_id),
  FOREIGN KEY (tag_id)
      REFERENCES Tag(tag_id),
  FOREIGN KEY (user_id)
      REFERENCES Users(user_id)
);

CREATE TABLE users_leave_comment(
  comment_id int4 AUTO_INCREMENT,
  user_id int4,
  PRIMARY KEY (comment_id, user_id),
  FOREIGN KEY (comment_id)
      REFERENCES Comments_photo(comment_id),
  FOREIGN KEY (user_id)
      REFERENCES Users(user_id)
);

CREATE TABLE friends(
  friend_one int4 ,
  friend_two int4 ,
  status ENUM('0', '1', '2') DEFAULT '0',
  PRIMARY KEY (friend_one, friend_two),
  FOREIGN KEY (friend_one) REFERENCES Users(user_id),
  FOREIGN KEY (friend_two) REFERENCES Users(user_id)
);

INSERT INTO Tag (tag) VALUES ('human');
INSERT INTO Tag (tag) VALUES ('science');
INSERT INTO Tag (tag) VALUES ('sightseeing');
INSERT INTO Tag (tag) VALUES ('animal');
INSERT INTO Tag (tag) VALUES ('universe');
INSERT INTO Tag (tag) VALUES ('plant');
INSERT INTO Tag (tag) VALUES ('cartoon');
