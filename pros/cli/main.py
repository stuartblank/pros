import logging
import os.path

import pros.common.sentry

import click
import click_completion
import sys

import pros.common.ui as ui
import pros.common.ui.log
from pros.cli.click_classes import *
from pros.cli.common import default_options, root_commands
from pros.common.utils import get_version, logger

root_sources = [
    'build',
    'conductor',
    'conductor_utils',
    'terminal',
    'upload',
    'v5_utils',
    'misc_commands',  # misc_commands must be after upload so that "pros u" is an alias for upload, not upgrade
    'interactive',
    'user_script'
]

if getattr(sys, 'frozen', False):
    exe_file = sys.executable
else:
    exe_file = __file__

if os.path.exists(os.path.join(os.path.dirname(exe_file), os.pardir, os.pardir, '.git')):
    root_sources.append('test')

for root_source in root_sources:
    __import__(f'pros.cli.{root_source}')


def main():
    try:
        ctx_obj = {}
        click_handler = pros.common.ui.log.PROSLogHandler(ctx_obj=ctx_obj)
        ctx_obj['click_handler'] = click_handler
        formatter = pros.common.ui.log.PROSLogFormatter('%(levelname)s - %(name)s:%(funcName)s - %(message)s', ctx_obj)
        click_handler.setFormatter(formatter)
        logging.basicConfig(level=logging.WARNING, handlers=[click_handler])
        cli.main(prog_name='pros', obj=ctx_obj)
        click_completion.init()
    except KeyboardInterrupt:
        click.echo('Aborted!')
    except Exception as e:
        logger(__name__).exception(e)


def version(ctx: click.Context, param, value):
    if not value:
        return
    ctx.ensure_object(dict)
    if ctx.obj.get('machine_output', False):
        ui.echo(get_version())
    else:
        ui.echo('pros, version {}'.format(get_version()))
    ctx.exit(0)

def install_callback(ctx, attr, value):
    if not value or ctx.resilient_parsing:
        return value
    shell, path = click_completion.core.install()
    click.echo('%s completion installed in %s' % (shell, path))
    exit(0)

@click.command('pros',
               cls=PROSCommandCollection,
               sources=root_commands)
@default_options
@click.option('--version', help='Displays version and exits', is_flag=True, expose_value=False, is_eager=True,
              callback=version)
@click.option('--install', help="Install completion for the current shell.", is_flag=True, expose_value=False, 
              callback=install_callback)
def cli():
    pros.common.sentry.register()


if __name__ == '__main__':
    main()
