/* generate the csv with candidate PRs */
/* Run in psql connected to gh_graphql_api:
   \copy (SELECT url, (select count(*) from "changedFiles" c where LOWER(COALESCE(SUBSTRING(c."fileName" FROM '\.([^.]+)$'), '')) = 'java' and c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as number_java_files, REPLACE(REPLACE(REGEXP_REPLACE(pr.title,'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' ') AS pr_title, REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(pr.body,'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') AS pr_body, pr."mergedAt", pr."mergedBy", pr.author, (select count(distinct login) from collaborators c where c.owner_repo = pr.owner_repo) as number_contributors, (select count(distinct login) from reviews c where c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as number_reviewers, (select REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(STRING_AGG(c.message, '|'),'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') from commits c where c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as commit_message, (select REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(STRING_AGG(c."bodyText", '|'),'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') from comments c where c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as comments_message, (select REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(STRING_AGG(r.body, '|'),'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') from reviews r where r.owner_repo = pr.owner_repo and r.pr_number = pr.pr_number) as reviewers_message FROM "pullRequests" pr WHERE (select count(*) from "changedFiles" c where LOWER(COALESCE(SUBSTRING(c."fileName" FROM '\.([^.]+)$'), '')) = 'java' and c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) > 0 AND pr.state = 'merged') TO 'candidateMergedReadabilityPRs.csv' CSV HEADER
*/

/* Standalone SELECT (for running in a GUI or without \copy): */
SELECT url,
	   (select count(*) from "changedFiles" c where LOWER(COALESCE(SUBSTRING(c."fileName" FROM '\.([^.]+)$'), '')) = 'java' and c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as number_java_files,	
	   REPLACE(REPLACE(REGEXP_REPLACE(pr.title,'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' ') AS pr_title,
       REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(pr.body,'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') AS pr_body,
       pr."mergedAt",
       pr."mergedBy",
       pr.author,
       (select count(distinct login) from collaborators c where c.owner_repo = pr.owner_repo) as number_contributors,
       (select count(distinct login) from reviews c where c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as number_reviewers, 
       (select REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(STRING_AGG(c.message, '|'),'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') from commits c where c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as commit_message,
       (select REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(STRING_AGG(c."bodyText", '|'),'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') from comments c where c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) as comments_message,
       (select REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(STRING_AGG(r.body, '|'),'[^\x20-\x7E]', ' ', 'g'),'\n',' '),'\r',' '),'<',' '),'-->',' '),'!--',' ') from reviews r where r.owner_repo = pr.owner_repo and r.pr_number = pr.pr_number) as reviewers_message
FROM "pullRequests" pr
WHERE (select count(*) from "changedFiles" c where LOWER(COALESCE(SUBSTRING(c."fileName" FROM '\.([^.]+)$'), '')) = 'java' and c.owner_repo = pr.owner_repo and c.pr_number = pr.pr_number) > 0
AND pr.state = 'merged';


/* verify how many pull requests does not change Java files */
SELECT count(*) FROM "pullRequests" pr
WHERE 
(SELECT count(*) 
 FROM "changedFiles" c 
 WHERE LOWER(COALESCE(SUBSTRING(c."fileName" FROM '\.([^.]+)$'), '')) = 'java' AND c.owner_repo = pr.owner_repo AND c.pr_number = pr.pr_number) = 0
AND pr.state = 'merged';


/* verify how many pull requests does not have at least 2 distinct logins (author and revisor) */
SELECT count(distinct prs.login), prs.owner_repo, prs.pr_number
FROM 
(
SELECT distinct login, owner_repo, pr_number
FROM reviews
WHERE (owner_repo, pr_number) IN (SELECT owner_repo, pr_number FROM "pullRequests" WHERE "mergedAt" IS NOT NULL)
UNION
SELECT distinct "mergedBy", owner_repo, pr_number
FROM "pullRequests" WHERE state = 'merged'
UNION
SELECT distinct author, owner_repo, pr_number
FROM "pullRequests" WHERE state = 'merged'
) prs
GROUP BY prs.owner_repo, prs.pr_number
HAVING count(distinct prs.login) = 1;
