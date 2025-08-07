import os
from phantom.utils.commands     import run
from phantom.utils.filesystem   import ensure_dirs, find_wsgi_folder, write_file
from phantom.utils.portfinder   import find_free_port
from phantom.utils.templates    import render_template_to_file
from phantom.defaults           import OS_PACKAGES, DEFAULT_DEBUG, generate_secret_key

class DeploymentError(Exception):
    def __init__(self, step, original):
        super().__init__(f"Error in {step}: {original}")
        self.step = step
        self.original = original

class DjangoDeployerAdapter:
    def __init__(self, ctx):
        self.ctx = ctx
        self.state = {}

    def deploy(self):
        try:
            self._ensure_directories()
            self._install_os_packages()
            self._clone_and_env()
            self._pip_install()
            if self.ctx['run_migrate']:
                self._migrate()
            if self.ctx['run_collectstatic']:
                self._collectstatic()
            self._find_bind_port()
            self._configure_supervisor()
            self._configure_nginx()
            self._finalize()
        except Exception as e:
            raise DeploymentError('deploy', e)

    def rollback(self):
        # remove created resources
        pass

    def _ensure_directories(self):
        try:
            ensure_dirs([self.ctx['project_path'], self.ctx['env_path']])
        except Exception as e:
            raise

    def _install_os_packages(self):
        try:
            run(['sudo', 'apt', 'update'])
            run(['sudo', 'apt', 'install', '-y'] + OS_PACKAGES)
        except Exception as e:
            raise

    def _clone_and_env(self):
        try:
            project_name = os.path.basename(self.ctx['repo_url']).replace('.git','')
            self.ctx['project_name'] = project_name
            run(['git', 'clone', self.ctx['repo_url'], f"{self.ctx['project_path']}/{project_name}"])
            run(['python3.12', '-m', 'venv', f"{self.ctx['env_path']}/{project_name}"])
            self.ctx['wsgi_module'] = find_wsgi_folder(f"{self.ctx['project_path']}/{project_name}")
        except Exception as e:
            raise

    def _pip_install(self):
        try:
            rp = f"{self.ctx['project_path']}/{self.ctx['project_name']}/requirements.txt"
            run(['bash','-lc',f"source {self.ctx['env_path']}/{self.ctx['project_name']}/bin/activate && pip install -r {rp} && pip install gunicorn"])
            env_file = os.path.join(self.ctx['project_path'], self.ctx['project_name'], '.env')
            content = f"DEBUG={DEFAULT_DEBUG}\nSECRET_KEY={generate_secret_key()}\n"
            write_file(env_file, content)
        except Exception as e:
            raise

    def _migrate(self):
        try:
            run(['bash','-lc',f"source {self.ctx['env_path']}/{self.ctx['project_name']}/bin/activate && cd {self.ctx['project_path']}/{self.ctx['project_name']} && python manage.py migrate"])
        except Exception as e:
            raise

    def _collectstatic(self):
        try:
            run(['bash','-lc',f"source {self.ctx['env_path']}/{self.ctx['project_name']}/bin/activate && cd {self.ctx['project_path']}/{self.ctx['project_name']} && python manage.py collectstatic --noinput"])
        except Exception as e:
            raise

    def _find_bind_port(self):
        try:
            port = self.ctx['port'] or find_free_port(8000,8010)
            self.ctx['port'] = port
        except Exception as e:
            raise

    def _configure_supervisor(self):
        try:
            cfg_path = f"/etc/supervisor/conf.d/{self.ctx['project_name']}.conf"
            render_template_to_file('supervisor/django.conf.j2', cfg_path, self.ctx)
            run(['sudo','supervisorctl','reread'])
            run(['sudo','supervisorctl','update'])
        except Exception as e:
            raise

    def _configure_nginx(self):
        try:
            cfg_path = f"/etc/nginx/sites-available/{self.ctx['project_name']}"
            render_template_to_file('nginx/django.conf.j2', cfg_path, self.ctx)
            run(['sudo','ln','-s',cfg_path,f"/etc/nginx/sites-enabled/{self.ctx['project_name']}"])
            run(['sudo','systemctl','restart','nginx'])
        except Exception as e:
            raise

    def _finalize(self):
        # set permissions, create logs dirs
        pass
