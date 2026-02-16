-- Run manually first: CREATE DATABASE gh_graphql_api;
-- Then connect to gh_graphql_api and run this script.
--
-- If repositories table already exists with overflow-prone columns, run:
-- ALTER TABLE repositories ALTER COLUMN architecture TYPE DECIMAL(15,8);
-- ALTER TABLE repositories ALTER COLUMN community TYPE DECIMAL(15,8);
-- ALTER TABLE repositories ALTER COLUMN continuous_integration TYPE DECIMAL(15,8);
-- ALTER TABLE repositories ALTER COLUMN documentation TYPE DECIMAL(15,8);
-- ALTER TABLE repositories ALTER COLUMN history TYPE DECIMAL(15,8);
-- ALTER TABLE repositories ALTER COLUMN issues TYPE DECIMAL(15,8);
-- ALTER TABLE repositories ALTER COLUMN license TYPE DECIMAL(15,8);
-- ALTER TABLE repositories ALTER COLUMN size TYPE DECIMAL(20,2);
-- ALTER TABLE repositories ALTER COLUMN unit_test TYPE DECIMAL(15,8);

CREATE TABLE IF NOT EXISTS repositories (
  owner_repo VARCHAR(255) NOT NULL,
  language VARCHAR(255) NOT NULL,
  stars INTEGER,
  "isFork" SMALLINT,
  "pullRequests" INTEGER,
  forks INTEGER,
  "numberIssues" INTEGER,
  watchers INTEGER,
  "lastUpdate" TIMESTAMP,
  scorebased_org DECIMAL(11,8),
  randomforest_org DECIMAL(10,8),
  scorebased_utl DECIMAL(11,8),
  randomforest_utl DECIMAL(10,8),
  architecture DECIMAL(15,8),
  community DECIMAL(15,8),
  continuous_integration DECIMAL(15,8),
  documentation DECIMAL(15,8),
  history DECIMAL(15,8),
  issues DECIMAL(15,8),
  license DECIMAL(15,8),
  size DECIMAL(20,2),
  unit_test DECIMAL(15,8),
  PRIMARY KEY (owner_repo)
);

CREATE TABLE IF NOT EXISTS "pullRequests" (
  owner_repo VARCHAR(255) NOT NULL,
  pr_number INTEGER NOT NULL,
  url VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  "mergedAt" TIMESTAMP,
  "mergedBy" VARCHAR(255),
  author VARCHAR(255) NOT NULL,
  state VARCHAR(255),
  PRIMARY KEY (owner_repo, pr_number),
  FOREIGN KEY (owner_repo) REFERENCES repositories(owner_repo)
);

ALTER TABLE "pullRequests" ADD COLUMN IF NOT EXISTS analysed SMALLINT DEFAULT 0;

CREATE TABLE IF NOT EXISTS comments (
  owner_repo VARCHAR(255) NOT NULL,
  pr_number INTEGER NOT NULL,
  "createdAt" TIMESTAMP NOT NULL,
  "bodyText" TEXT NOT NULL,
  author VARCHAR(255) NOT NULL,
  PRIMARY KEY (owner_repo, pr_number, "createdAt"),
  FOREIGN KEY (owner_repo, pr_number) REFERENCES "pullRequests"(owner_repo, pr_number)
);

CREATE TABLE IF NOT EXISTS commits (
  owner_repo VARCHAR(255) NOT NULL,
  pr_number INTEGER NOT NULL,
  url VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  author VARCHAR(255) NOT NULL,
  PRIMARY KEY (owner_repo, pr_number, url),
  FOREIGN KEY (owner_repo, pr_number) REFERENCES "pullRequests"(owner_repo, pr_number)
);

CREATE TABLE IF NOT EXISTS "changedFiles" (
  owner_repo VARCHAR(255) NOT NULL,
  pr_number INTEGER NOT NULL,
  "fileName" VARCHAR(500) NOT NULL,
  "typeChange" VARCHAR(255) NOT NULL,
  PRIMARY KEY (owner_repo, pr_number, "fileName"),
  FOREIGN KEY (owner_repo, pr_number) REFERENCES "pullRequests"(owner_repo, pr_number)
);

CREATE TABLE IF NOT EXISTS repository_search_log (
  owner_repo VARCHAR(255) NOT NULL,
  keyword VARCHAR(255),
  number_results INTEGER NOT NULL,
  error TEXT,
  PRIMARY KEY (owner_repo, keyword),
  FOREIGN KEY (owner_repo) REFERENCES repositories(owner_repo)
);

CREATE TABLE IF NOT EXISTS collaborators (
  owner_repo VARCHAR(255) NOT NULL,
  id INTEGER NOT NULL,
  login VARCHAR(255) NOT NULL,
  type VARCHAR(255) NOT NULL,
  site_admin SMALLINT NOT NULL,
  contributions INTEGER NOT NULL,
  PRIMARY KEY (owner_repo, id),
  FOREIGN KEY (owner_repo) REFERENCES repositories(owner_repo)
);

CREATE TABLE IF NOT EXISTS reviews (
  id SERIAL PRIMARY KEY,
  owner_repo VARCHAR(255) NOT NULL,
  pr_number INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  login VARCHAR(255) NOT NULL,
  type VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  site_admin SMALLINT NOT NULL,
  state VARCHAR(255) NOT NULL,
  author_association VARCHAR(255) NOT NULL,
  FOREIGN KEY (owner_repo, pr_number) REFERENCES "pullRequests"(owner_repo, pr_number)
);
