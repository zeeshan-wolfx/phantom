import os



def ensure_dirs(paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def find_wsgi_folder(project_dir):
    for root, dirs, files in os.walk(project_dir):
        if 'wsgi.py' in files:
            module = os.path.basename(root)
            return f"{module}.wsgi"
    raise FileNotFoundError('wsgi.py not found')