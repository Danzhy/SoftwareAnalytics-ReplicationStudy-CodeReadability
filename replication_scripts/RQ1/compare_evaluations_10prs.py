import pandas as pd

our_file = "../../outputs/reviewed10_prs.xlsx"
adriano_file = "../../datasets/Adriano Evaluation Merged PRs.xlsx"
carlos_file = "../../datasets/Carlos Evaluation  Merged PRs.xlsx"

our_df = pd.read_excel(our_file)
adriano_df = pd.read_excel(adriano_file)
carlos_df = pd.read_excel(carlos_file)

our_pr_col = next(col for col in our_df.columns if "Pull Request" in col)

adriano_pr_col = next(col for col in adriano_df.columns if "Pull Request" in col)
adriano_type_col = next(col for col in adriano_df.columns if "Type of Code Change" in col)

carlos_pr_col = next(col for col in carlos_df.columns if "Pull Request" in col)
carlos_type_col = next(col for col in carlos_df.columns if "Type of Code Change" in col)

adriano_eval = adriano_df[adriano_df[adriano_pr_col].isin(our_df[our_pr_col])]
carlos_eval = carlos_df[carlos_df[carlos_pr_col].isin(our_df[our_pr_col])]

adriano_eval = adriano_eval.drop_duplicates(subset=[adriano_pr_col])
carlos_eval = carlos_eval.drop_duplicates(subset=[carlos_pr_col])

adriano_eval = adriano_eval[[adriano_pr_col, adriano_type_col]]
adriano_eval.columns = ["Pull Request", "Adriano Classification"]

carlos_eval = carlos_eval[[carlos_pr_col, carlos_type_col]]
carlos_eval.columns = ["Pull Request", "Carlos Classification"]

merged_df = our_df.merge(adriano_eval, on="Pull Request", how="left")
merged_df = merged_df.merge(carlos_eval, on="Pull Request", how="left")

output_file = "../../outputs/reviewed10_prs_with_evaluations.xlsx"
merged_df.to_excel(output_file, index=False)

print(f"Excel file created: {output_file}")