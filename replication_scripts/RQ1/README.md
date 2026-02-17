## Replication Guide: RQ1

**“Do the PRs labeled as readability improvements truly represent code readability changes?”**

This guide explains how we replicated **RQ1** by manually reviewing a random subset of PRs from the original dataset and comparing our classifications with those provided by the original authors and additional reviewers.

---

## Overview

The original dataset contains **401 merged Pull Requests (PRs) commits** that were classified by the authors as *code readability improvements*.  For this replication we performed the following:
- Randomly sampled **10 PRs** using `select10PRs.py` script from the 401 commits
- Manually reviewed them for readability improvements
- Compare our judgments with existing reviewer classifications
- Assess agreement and understand the authors’ coding guidelines
---

### Part 1: Random Sampling of Readability PRs

This step randomly selects 10 PRs from the original dataset using `select10PRs.py` and create an xlms sheet in output folder for manual inspection.

**Note** Running this will generate a new sample, we have included it to show our process.


### Part 2: Manual Review and Classification

1. Open `sampled10_prs.xlsx`.
2. Manually inspect each PR by reading:
    - The developer’s description
    - The code changes
3. Decide whether each PR genuinely represents a **code readability improvement**. and suggect a classification.
4. Record your judgment in a new file:
5. Our sample and classification can be found in  `outputs/sampled10_prs.csv` and  `outputs/reviewed10_prs.csv` respectively


### Part 3: Comparison with Other Reviewers

1. To assess agreement and differences in interpretation, we compare our manual classifications with two original independent reviewer datasets.

2. The classifications of all the PRs can be found in:

    - `datasets/Adriano Evaluation Merged PRs.xlsx`
    - `datasets/Carlos Evaluation  Merged PRs.xlsx`

3. Run the `compare_evaluations_10prs.py` script to filter your samples PRs and compare with the Original Authors classification.
4. Results will be created in `outputs/reviewed10_prs_with_evaluations.xlsx`

### Results
Our manual review demonstrated that our classification is fundamentally the same as the authors'. Based on the high similarity observed across the 10 randomly selected PRs, we believe the original authors' classifications are highly accurate and reliable.

Detailed analysis can be found at  `outputs/RQ1analysis.md`