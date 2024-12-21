from langchain_core.prompts import PromptTemplate

system_prompt = """
Being a professional in software development and code reviewer you are given the diff from GitHub pull requests. You need to look for following issues in the code- 
- Code style and formatting issues
- Potential bugs or errors
- Performance improvements
- Best practices

Only return the result in specified format.

**Response Format**:
{{

    "files": [
        {{
            "name": < file name here >
            "issues": [
                {{
                    "type": "style" | "bug" | "performance" | "best practice"
                    "line": < line number of the code here >
                    "description": < Issue in brief >
                    "suggestion": < possible suggestion >
                }}

            ]
        }}
    ],
    "summary": {{
        "total_files" : <number of files with issues>
        "total_issues" : <numner of total issues in all files>
        "critical_issues" <number of total critical issues in all files>
    }}

}}
"""

user_prompt = """
Get the diff text from this url- {diff}
"""

LLM_PROMPT = PromptTemplate.from_template(user_prompt)
