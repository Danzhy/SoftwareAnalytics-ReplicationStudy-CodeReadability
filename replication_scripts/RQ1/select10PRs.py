import pandas as pd

file_path = "../../datasets/Selected Merged PRs with code readabiliy improvements.xlsx"
df = pd.read_excel(file_path)

sampled_df = df.sample(n=10)

pr_col = next(col for col in df.columns if "Pull Request" in col)
desc_col = next(col for col in df.columns if "Developer" in col)
code_col = next(col for col in df.columns if "Code" in col)


output_df = sampled_df[[pr_col, desc_col, code_col]]
output_df.columns = ["Pull Request", "Developer Description", "Code Change"]

output_file = "../../outputs/sampled10_prs.xlsx"
output_df.to_excel(output_file, index=False)

print(f"Excel file created: {output_file}")