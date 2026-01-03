import os
import jinja2
import subprocess

def write_file(file_path, content):
    with open(file_path, "w") as f:
        f.write(content)

def save_latex_as_pdf(tex_path, dst_path):
    output_dir = os.path.dirname(dst_path)
    # Run pdflatex. Using nonstopmode to prevent hanging on errors.
    # Output directory must exist.
    cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={output_dir}", tex_path]
    
    print(f"Running command: {' '.join(cmd)}")
    try:
        # Run twice to resolve references/page numbers if needed
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error compiling LaTeX: {e}")
        print(f"Stdout: {e.stdout.decode('utf-8')}")
        print(f"Stderr: {e.stderr.decode('utf-8')}")

def escape_for_latex(data):
    if isinstance(data, dict):
        new_data = {}
        for key in data.keys():
            new_data[key] = escape_for_latex(data[key])
        return new_data
    elif isinstance(data, list):
        return [escape_for_latex(item) for item in data]
    elif isinstance(data, str):
        latex_special_chars = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\^{}",
            "\\": r"\textbackslash{}",
            "\n": "\\newline%\n",
            "-": r"{-}",
            "\xA0": "~",
            "[": r"{[}",
            "]": r"{]}",
        }
        return "".join([latex_special_chars.get(c, c) for c in data])

    return data


# defining function that are called in the template
def richtext_to_latex(richtext_dict: dict) -> str:
    if isinstance(richtext_dict, str):
        return richtext_dict
    if not richtext_dict or not isinstance(richtext_dict, dict):
        return ""
    response = []
    segments = richtext_dict.get("segments", [])
    for segment in segments:
        content = segment.get("content", "")
        if segment.get("type") == "text":
            response.append(content)
        elif segment.get("type") == "link":
            url = segment.get("url", "")
            response.append(rf"\href{{{url}}}{{{content}}}")
    return " ".join(response)

def json_to_latex_pdf(json_resume, dst_path, template_name = "resume.tex.jinja"):
    try:
        module_dir = os.path.dirname(__file__)
        templates_path = os.path.join(os.path.dirname(module_dir), 'templates')

        latex_jinja_env = jinja2.Environment(
            block_start_string="\\BLOCK{",
            block_end_string="}",
            variable_start_string="\\VAR{",
            variable_end_string="}",
            comment_start_string="\\#{",
            comment_end_string="}",
            line_statement_prefix="%-",
            line_comment_prefix="%#",
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader(templates_path),
        )

        # add the functions to the template
        latex_jinja_env.globals.update(richtext_to_latex=richtext_to_latex)
        latex_jinja_env.globals.update(len=len)

        escaped_json_resume = escape_for_latex(json_resume)
        
        try:
            resume_template = latex_jinja_env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            print(f"Template {template_name} not found in {templates_path}")
            return None, None

        resume_latex = resume_template.render(escaped_json_resume)

        tex_path = dst_path.replace(".pdf", ".tex")

        write_file(tex_path, resume_latex)
        save_latex_as_pdf(tex_path, dst_path)
        
        print(f"PDF generated at: {dst_path}")
        return dst_path, tex_path
    except Exception as e:
        print(f"Error in json_to_latex_pdf: {e}")
        return None, None

