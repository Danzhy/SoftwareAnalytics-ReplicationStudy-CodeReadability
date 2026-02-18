## 1. Project Title and Overview

- **Paper Title:** *How Do Developers Improve Code Readability? An Empirical Study of Pull Requests*
- **Authors:** Carlos Eduardo C. Dantas, Adriano M. Rocha, Marcelo A. Maia
- **Replication Team:** Daniar Zhylangozov, Nelson Mbigili
- **Course:** CS-UH 3260 Software Analytics
- **Institution:** NYU Abu Dhabi

### Brief Description

#### Original Paper Summary
Dantas, Rocha, and Maia (2023) analyzed 311 pull requests across 109 Java repositories to examine how developers manually improve code readability. The study introduced a taxonomy of 26 distinct readability improvement types and highlighted a major gap in automated tool support. Specifically, the static analysis tool SonarQube detected only 7% of the readability improvements performed by developers.

#### Replication Study Summary
This replication study reproduces the original research by validating the 26-type readability improvement taxonomy and reassessing the SonarQube detection gap using the original dataset. The study also extends the original work through a longitudinal analysis of more recent development practices. It is structured into three phases:

- **Manual Calibration (RQ1):**  
  A qualitative review of 10 randomly selected pull requests to align with the original authors’ coding guidelines and ensure consistent application of the taxonomy.

- **Technical Reproduction (RQ2):**  
  A re-analysis of all 311 original pull requests using SonarQube to verify the reported limitations of static analysis tools in detecting human-driven readability improvements.

- **Longitudinal Extension:**  
  Mining recent pull requests from 5 selected repositories and applying closed coding to examine how the distribution of readability improvement types has evolved over time.

## 2. Repository Structure

```
root/
├── README.md
├── requirements.txt
├── .env                    # DB and GitHub credentials (create per Setup Instructions; not committed)
├── datasets/               # Datasets from the artifact
│   └── fileTemp/           # SonarQube analysis results (before/after) for RQ2
├── replication_scripts/    # Scripts for steps 1.1–1.7 and RQ1/RQ2
├── outputs/                # Generated results
├── logs/                   # Screenshots of errors and script outputs
└── notes/                  # Notes taken during execution and fixes
```

### datasets/

Contains datasets provided in the original artifact, **except** `reaper-dataset.csv`, which is provided separately because it is too large.

- **fileTemp/** — Result of extracting code readability issues identified by SonarQube. Each subfolder (e.g., `2`, `16`, `95`) corresponds to a pull request and contains `sonarLintAnalysis_before.csv` and `sonarLintAnalysis_after.csv`. These were provided in the artifact and are used by the RQ2 `CountOccurrences.java` script.
- Excell sheets and csv files used in **RQ2**

### logs/

Contains screenshots of errors and outputs from running scripts in steps 1.1–1.6 and the RQ2 scripts. Examples include MySQL/PostgreSQL migration errors, `repoInfo.py` NoneType/DatatypeMismatch errors, and successful run outputs.

### outputs/

Generated results from the replication:

- **RQ2 parsing** — Screenshot and CSV of the formatted table comparing SonarQube issues before vs. after commits (output of `parseOutput.py`).
- **candidateMergedReadabilityPRs.csv** — Result of selecting 5 repos and mining their merged readability-related PRs (output of `query.sql` in step 1.7).
- **Extended study - Classifications - Sheet1.csv** - Result of manualy analyzing merged readability-related PRs from candidateMergedReadabilityPRs.csv
- **BeforeandAfter** Code files we mines (Some are missing with error.txt messages due to broken github links or other reasons)
- Excell sheets and csv files for evaluation of RQ1
- ReadabilityIssues count from sonar analysis in a csv file


### replication_scripts/

Scripts for the replication pipeline:

- **1.1 import reaper dataset/** — `importReaper_modified.py` (imports reaper CSV into PostgreSQL), `script_schema.sql` (database schema). We only imported approximately 30k repositories.
- **1.2 import repository information/** — `repoInfo.py` (fetches repo metadata from GitHub GraphQL).
- **1.3 import pull requests/** — `importPullRequests.py` (imports merged PRs matching readability keywords).
- **1.4 changed files/** — `changedFiles.py` (fetches changed files per PR).
- **1.5 collaborators/** — `collaborators.py` (fetches contributors per repo).
- **1.6 reviews/** — `reviews.py` (fetches PR reviews).
- **1.7 generate csv/** — `query.sql` (generates `candidateMergedReadabilityPRs.csv`).
- **RQ1/** — `README.md` With detailed steps of the replication	and results, `select10PRs.py` scrip used to get random prs for manual review and `compare_evaluations_10prs.py` to compare our close coding to original authors
- **RQ2/** — `CountOccurrences.java` (counts SonarQube rule violations before/after), `parseOutput.py` (parses Java output into a table and CSV), `rq2_readability_issues.csv` (generated output), `download_before_and_after.py` Downloads before and after code files from github (our dataset inside outputs),`sonarlint-core-master` static analysis to suggested code improvements, `READE.md` Document the steps.


Please find more detailed explanation of changes made to scripts in the `/notes/Script changes.txt`

### notes/

- **NOTES.txt** — Notes taken while executing scripts, encountering errors, and applying fixes.

## 3. Setup Instructions

### 3.1 Python

- **Version:** Python 3.13 was used for this replication. Python 3.9+ should work; earlier versions are untested.
- **Virtual environment (recommended):**
  ```bash
  #Run from root directory
  python3 -m venv venv
  source venv/bin/activate   # On Windows: venv\Scripts\activate
  ```
- **Dependencies:** Install from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```
  Dependencies include: `psycopg2-binary`, `python-dotenv`, `PyGithub`, `requests`, `pandas`.

### 3.2 Java

- **Version:** Java 22.0.1 was used (OpenJDK or Oracle JDK).
- **Installation:**
  - **macOS (Homebrew):** `brew install openjdk@22`
  - **Windows/Linux:** Download from [Adoptium](https://adoptium.net/) or [Oracle](https://www.oracle.com/java/technologies/downloads/)
  - Verify: `java -version` and `javac -version`

### 3.3 PostgreSQL

- **Requirement:** A local PostgreSQL server must be running.
- **Installation:** Download and install from [postgresql.org](https://www.postgresql.org/download/).
- **Create the database** (in `psql` or any PostgreSQL client):
  ```sql
  CREATE DATABASE gh_graphql_api;
  ```
- **Apply the schema** (run from the root directory):
  ```bash
  psql -U postgres -d gh_graphql_api -f "replication_scripts/1.1 import reaper dataset/script_schema.sql"
  ```

### 3.4 Environment Variables (.env)

Create a `.env` file in the root directory with:

```
DB_HOST=localhost
DB_NAME=gh_graphql_api
DB_USER=postgres
DB_PASSWORD=your_password
GITHUB_ACCESS_TOKEN=your_github_personal_access_token
```

- **DB_HOST:** PostgreSQL host (usually `localhost`)
- **DB_NAME:** Database name (`gh_graphql_api`)
- **DB_USER:** PostgreSQL username (can use superuser, which is usually `postgres`)
- **DB_PASSWORD:** PostgreSQL password (for the specific user)
- **GITHUB_ACCESS_TOKEN:** Required for GitHub API calls. Create one at [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens) with `repo` scope.

### 3.5 Quick Setup Checklist

1. Install Python 3.9+, Java 22 (or compatible), and PostgreSQL
2. Create virtual environment: `python3 -m venv venv` and activate it
3. Install Python deps: `pip install -r requirements.txt`
4. Create PostgreSQL database: `CREATE DATABASE gh_graphql_api;`
5. Run schema: `psql -U postgres -d gh_graphql_api -f "replication_scripts/1.1 import reaper dataset/script_schema.sql"`
6. Create `.env` with DB and GitHub credentials
7. Place `reaper-dataset.csv` in the root folder for the import step

### 3.6 Running scripts 

Run all scripts **apart from RQ1** from the root folder.

**Python scripts (steps 1.1–1.6):**
```bash
python "replication_scripts/1.1 import reaper dataset/importReaper_modified.py"
python "replication_scripts/1.2 import repository information/repoInfo.py"
python "replication_scripts/1.3 import pull requests/importPullRequests.py"
python "replication_scripts/1.4 changed files/changedFiles.py"
python "replication_scripts/1.5 collaborators/collaborators.py"
python "replication_scripts/1.6 reviews/reviews.py"
```

**Step 1.7 — Generate CSV based on `query.sql`:** Run via the `psql` terminal.

1. From the root folder, connect to the database:
   ```bash
   psql -U postgres -d gh_graphql_api
   ```


2. To export the main query result to `candidateMergedReadabilityPRs.csv`, the `\copy` command is in the comment at the top of `query.sql`. Copy that full `\copy (SELECT ... ) TO 'candidateMergedReadabilityPRs.csv' CSV HEADER` line, paste it into the `psql` prompt, and run it. The CSV is written to the directory where you started `psql` (the root folder). To save it in `outputs/`, either `cd outputs` before starting `psql`, or move the file afterward.

We couldn't figure out how to use the query.sql directly to export the results to csv file.
Thus based on the query.sql the command \copy ... basically performs the same filtering and writes it onto csv.

**For RQ1 scripts (compare_evaluations_10prs.py and select10PRs.py):**  
Either `cd` into `replication_scripts/RQ1/` first, or adjust the paths in those scripts.



## 4. GenAI Usage

**Cursor** , **ChatGPT** were used for understanding scripts and debugging, and basically as documentation assistants.

- **Understanding and migrating SQL:** We used Cursor to explain what the unique MySQL syntax lines are in `.sql` queries and scripts. Cursor was then used as "documentation" to figure out how to replace MySQL-specific syntax in `.sql` files and DB connection logic in scripts. This way we were able to promptly ensure that scripts support PostgreSQL, not MySQL.

- **Formatting documentation:** We used prompts like "how to create lists, how to create embedded code blocks, how to make text bold" to format `.md` files.

- **Debugging errors:** When we encountered errors we asked Cursor and ChatGPT why those errors occurred. For example, we asked why we encountered "NoneType" and "DatatypeMismatch" ([Screenshot](/logs/ERROR:%20repoInfo%20isFork%20field%20and%20NoneType.png)) errors when running `repoInfo.py` for the first time. Based on the output we changed how we handled missing values and `isFork` column values, which made the script run correctly.


## Grading Criteria for README

Your README will be evaluated based on the following aspects (Total: 40 points):

### 1. Completeness (10 points)
- [ ] All required sections are present
- [ ] Each section contains sufficient detail
- [ ] Repository structure is fully documented
- [ ] All files and folders are explained
- [ ] GenAI usage is documented (if any AI tools were used)

### 2. Clarity and Organization (5 points)
- [ ] Information is well-organized and easy to follow
- [ ] Instructions are clear and unambiguous
- [ ] Professional writing and formatting
- [ ] Proper use of markdown formatting (headers, code blocks, lists)

### 3. Setup and Reproducibility (10 points)
- [ ] Setup instructions are complete and accurate, i.e., we were able to rerun the scripts following your instructions and obtain the results you reported


## Best Practices

1. **Be Specific**: Include exact versions, paths, and commands rather than vague descriptions
2. **Keep It Updated**: Ensure the README reflects the current state of your repository
3. **Test Your Instructions**: Have someone else (or yourself in a fresh environment) follow the setup instructions
4. **Document AI Usage**: If you used any GenAI tools, be transparent about how they were used (e.g., understanding scripts, exploring datasets, understanding data fields)


## Acknowledgement

This guideline was developed with the assistance of [Cursor](https://www.cursor.com/), an AI-powered code editor. This tool was used to:

- Draft and refine this documentation iteratively