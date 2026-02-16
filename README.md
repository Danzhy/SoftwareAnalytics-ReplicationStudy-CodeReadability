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

Document your repository structure clearly. Organize your repository using the following standard structure:

```
README                    # Documentation for your repository
datasets/                 # Subset of data you used (if any). If you used the whole dataset, include instructions on how to download it
replication_scripts/      # Scripts used in your replication:
                          #   - If you used scripts as-is: document which scripts you ran
                          #   - If you modified scripts: include the modified scripts
                          #   - If you created new scripts: include all new scripts
outputs/                  # Your generated results only
logs/                     # Console output, errors, screenshots
notes/                    # Optional if you have any notes you took during reproduction (E.g., where you noted discrepencies etc)
```

**For each folder and file, provide a brief description of what it contains.**

## 3. Setup Instructions

- **Prerequisites**: Required software, tools, and versions
  - OS requirements
  - Programming language versions (Python, R, etc.)
  - Required packages/libraries and versions
  - Any other dependencies
- **Installation Steps**: Step-by-step instructions to set up the environment
  - How to install dependencies
  - How to configure paths or settings
  - Any environment variables needed

## 4. GenAI Usage

**GenAI Usage**: Briefly document any use of generative AI tools (e.g., ChatGPT, GitHub Copilot, Cursor) during the replication process. Include:

  - Which tools were used
  - How they were used (e.g., understanding scripts, exploring datasets, understanding data fields, debugging)
  - Brief description of the assistance provided


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
