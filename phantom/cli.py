import click

from phantom.adapters.django    import DjangoDeployerAdapter
from phantom.utils.logger       import setup_logger

@click.group()
def cli():
    pass

@cli.command()
@click.option('--cascade-on-fail', is_flag=True, default=False, help='Cleanup on failure')
def init(cascade_on_fail):
    """Initialize a new Phantom deployment"""
    # Prompt for inputs
    url = click.prompt('GitHub repo URL', type=str)
    project_path = click.prompt('Project path', default='/home/ubuntu/project')
    env_path = click.prompt('Env path', default='/home/ubuntu/project_env')
    domain = click.prompt('IP or domain name', type=str)
    port = click.prompt('Port (leave blank to auto-find)', default='', show_default=False)
    run_migrate = click.confirm('Run migrate?', default=True)
    run_collectstatic = click.confirm('Run collectstatic?', default=True)

    ctx = {
        'repo_url': url,
        'project_path': project_path,
        'env_path': env_path,
        'domain': domain,
        'port': int(port) if port else None,
        'run_migrate': run_migrate,
        'run_collectstatic': run_collectstatic,
        'cascade_on_fail': cascade_on_fail,
    }
    setup_logger()
    adapter = DjangoDeployerAdapter(ctx)
    try:
        adapter.deploy()
        click.echo('Deployment completed successfully.')
    except Exception as e:
        click.echo(f'Deployment failed: {e}')
        if cascade_on_fail:
            adapter.rollback()
        raise

def main():
    cli()

if __name__ == '__main__':
    cli()