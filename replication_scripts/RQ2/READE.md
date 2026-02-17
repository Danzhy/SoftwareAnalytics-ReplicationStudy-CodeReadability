## Replication Guide: RQ2
**"Do developers fix code readability issues identified by SonarQube in readability PRs?"**

This guide provides instructions on how to:
- Download the "Before" and "After" versions of Java classes from GitHub.
- Run SonarQube locally to get static analysis of the "Before" and "After" files.
- Create a simple table to analyze the findings.

---

### Part 1: Data Acquisition (GitHub Download)

This phase uses the provided Python script to pull the specific Java files that were modified in the readability PRs. 

**Note:** While we have provided a Python script to download files directly from GitHub, for this specific replication, we decided to use the ** original provided data within the dataset**. This choice was made because several original GitHub links in the source data were missing or returned 404 errors, making a full download inconsistent.

#### Steps to Download:
1. **Environment**: Ensure you have a `.env` file in your root directory with your `GITHUB_ACCESS_TOKEN`.
2. **Dataset**: The script uses the `Selected Merged PRs with code readabiliy improvements.csv` in the `../../datasets/` directory.
3. **Run the Script**: Execute the Python script. The script will:
    * Read each row of the CSV.
    * Parse the GitHub URL to identify the repository and the "After" commit SHA.
    * Call the GitHub API to find the "Parent SHA" (the "Before" state).
    * Download the raw `.java` file for both commits.

#### Results:
All downloaded files are organized within the `../../outputs/beforeandafter/` directory. For every PR processed, the script creates a numbered folder (starting from `2`) with the following structure:

```text
outputs/beforeandafter/
└── [Folder_ID]/
    ├── before/
    │   └── TargetClass.java  <-- Original version with issues
    ├── after/
    │   └── TargetClass.java  <-- Fixed version after PR
    └── error.txt             <-- Only created if a download fails
```

### Part 2: Static Analysis (Local SonarQube via SonarLint Core)

In this step, we use the **SonarLint Core** engine to perform static analysis. Instead of a full server GUI, we execute the analysis directly through a specialized test class using **VS Code** and the **Terminal**.

### Prerequisites
- **JDK 17 or 21**: Necessary to run the SonarLint Core project.
- **Maven**: To build the project and handle dependencies.
- **Spring Tool Suite (STS)**: The recommended IDE for importing and executing the SonarLint Core Maven project.
- **VS Code**: For navigating the file system and initial configuration.

#### Instructions to Run Analysis:

1. **Setting Up**: 
   - Go to `replication_scripts/RQ2/sonarlint-core-master/`
   - Find the StandaloneIssueMediumTests4.java file. 
   - Use the terminal to locate it: `find . -name "StandaloneIssueMediumTests4.java"`
   - In the file, change **rootDir** path to reflect path to fileTemp (Original dataset). In the project file you it can be found at `./datasets/fileTemp`

2. **Execute the Analysis**:
   - From the root of `sonarlint-core-master`, run the following command in your terminal to compile the engine:
   ```bash
   ./mvnw clean install -DskipTests
   ```
   - Run the analysis engine using the specialized test class. This will process your before and after files:
   ```bash
   ./mvnw -pl core -Dtest=StandaloneIssueMediumTests4 test
   ```

#### Results
The analysis engine will generate two key files inside each of the file:
```
 datasets/fileTemp/2/before:
    - sonarLintAnalysis_before.csv
    - sonarLintAnalysis_after.csv

 datasets/fileTemp/2/after:
    - sonarLintAnalysis_before.csv
    - sonarLintAnalysis_after.csv

```

---

### Part 3: Comparative Analysis & Table Generation

The final step is to merge the findings into a comparative table to answer the research question.

---