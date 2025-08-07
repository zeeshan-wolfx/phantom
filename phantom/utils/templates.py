
import os
from jinja2 import Environment, FileSystemLoader



def render_template_to_file(template_path, target_path, context):
    base = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(base))
    tpl = env.get_template(template_path)
    content = tpl.render(**context)
    with open(target_path, 'w') as f:
        f.write(content)