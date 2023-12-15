#!/usr/bin/python3

import typer
from typing_extensions import Annotated

from rich import print
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

import os
import datetime
import importlib.metadata

from devchain_toolchains import ToolchainStatus
from devchain_toolchains import ToolchainInfo

from devchain_toolchains import Cpp as CppToolchain
from devchain_toolchains import Result


app = typer.Typer()


###############################################################################
# HELPER METHODS
###############################################################################


def get_toolchain(path: str):
    '''
    Gets the toolchain for this directory.

        Parameters:
            path (str):  Path to the related directory
        Returns:
            Toolchain
    '''
    cpp = CppToolchain(path)
    if cpp.info().status == ToolchainStatus.AVAILABLE:
        return cpp

    # TODO(gfischer) Add support for other toolchains

    return None


def get_toolchain_info(path: str) -> ToolchainInfo:
    '''
    Collects all information about the given directory.

        Parameters:
            path (str):  Path to the directory that shall be checked
        Returns:
            Toolchain information
    '''
    toolchain_info = ToolchainInfo()

    toolchain = get_toolchain(path)
    if toolchain is not None:
        toolchain_info = toolchain.info()

    return toolchain_info


def log_command_info(result: Result,
                     ts_start: datetime.datetime,
                     ts_end: datetime.datetime) -> None:
    table_info = Table(show_header=False,
                       box=None,
                       style='white')
    table_info.add_column('', style='white')
    table_info.add_column('', style='white')
    for k, v in result.info.items():
        table_info.add_row(k, v)

    table_info.add_row('', '')
    table_info.add_row('runtime', str(ts_end - ts_start))

    group = Group(
        Panel(result.message, style='white'),
        Panel(table_info, style='white')
    )
    print(Panel.fit(group,
                    title='[bold] Result [/bold]',
                    style=('green' if result.ok() else 'red')))


###############################################################################
# COMMAND AUTO-COMPLETIONS
###############################################################################

def complete_create_toolchain() -> list[str]:
    return ['cpp']


def complete_build_settings() -> list[str]:
    path = os.path.abspath(os.getcwd())
    toolchain_info = get_toolchain_info(path)
    for build_opt in toolchain_info.build_opts:
        if build_opt.name == 'settings':
            return build_opt.values
    return []


def complete_run_tool() -> list[str]:
    path = os.path.abspath(os.getcwd())
    toolchain_info = get_toolchain_info(path)
    for run_opt in toolchain_info.run_opts:
        if run_opt.name == 'tool':
            return run_opt.values
    return []


###############################################################################
# TOOL COMMANDS
###############################################################################

@app.command()
def about():
    '''
    Returns information about this application.
    '''
    metadata = importlib.metadata.metadata('devchain')
    table = Table(show_header=False, box=None, style='white')
    table.add_column('')
    table.add_column('')
    table.add_row('Name', metadata['Name'], style='white')
    table.add_row('Summary', metadata['Summary'], style='white')
    table.add_row('Author', metadata['Author'], style='white')
    table.add_row('Version', metadata['Version'], style='white')

    print(Panel.fit(table,
                    title='[bold] About [/bold]',
                    style="cyan"))


@app.command()
def info():
    '''
    Collects and prints all information about the current directory.
    '''
    path = os.path.abspath(os.getcwd())
    toolchain_info = get_toolchain_info(path)

    # Common information
    common_info = '\n[bold yellow]path[/]      [white]{}[/]'.format(path)
    common_info += '\n[bold yellow]toolchain[/] [white]{}[/]'.format(
        toolchain_info.name)
    common_info += '\n'

    if toolchain_info.status is ToolchainStatus.NOT_AVAILABLE:
        print(Panel.fit(common_info,
                        title='[bold] Info [/bold]',
                        style="cyan"))
        return

    # Build options
    build_opts_table = Table(show_header=False,
                             box=None)
    build_opts_table.add_column('')
    build_opts_table.add_column('')
    for build_opt in toolchain_info.build_opts:
        build_opts_table.add_row(build_opt.name, '\n'.join(build_opt.values))

    # Run options
    run_opts_table = Table(show_header=False,
                           box=None)
    run_opts_table.add_column('')
    run_opts_table.add_column('')
    for run_opt in toolchain_info.run_opts:
        run_opts_table.add_row(run_opt.name, '\n'.join(run_opt.values))

    # Create output
    group = Group(
        common_info,
        Panel(build_opts_table,
              title='Build Options',
              padding=0,
              style='white'
              ),
        Panel(run_opts_table,
              title='Run Options',
              padding=0,
              style='white'
              )
    )
    print(Panel.fit(group,
                    title='[bold] Info [/bold]',
                    style="cyan"))


@app.command()
def create(
        toolchain: Annotated[
            str,
            typer.Option(
                "--toolchain", "-t",
                help='Toolchain to be created',
                autocompletion=complete_create_toolchain
            )
        ],
        force: Annotated[
            bool,
            typer.Option(
                "--force", "-f",
                help='Force creation even if directory is not empty'
            )
        ] = False
):
    '''
    Creates a project template in the current directory.
    '''
    ts_start = datetime.datetime.now()

    path = os.path.abspath(os.getcwd())

    if toolchain == 'cpp':
        cpp = CppToolchain(path)
        result = cpp.create(force)
    else:
        print('[bold red]:boom: Invalid toolchain ({})'.format(toolchain))
        return

    ts_end = datetime.datetime.now()

    log_command_info(result, ts_start, ts_end)


@app.command()
def clean():
    '''
    Cleans all build artifacts.
    '''
    ts_start = datetime.datetime.now()

    path = os.path.abspath(os.getcwd())
    toolchain = get_toolchain(path)
    result = toolchain.clean()

    ts_end = datetime.datetime.now()

    log_command_info(result, ts_start, ts_end)


@app.command()
def build(
        settings: Annotated[
            str,
            typer.Option(
                "--settings", "-s",
                help='Settings to be used',
                autocompletion=complete_build_settings
            )
        ],
        verbose: Annotated[
            bool,
            typer.Option(
                "--verbose", "-v",
                help='Enable verbose output'
            )
        ] = False
):
    '''
    Builds the project in the current diretory.
    '''
    ts_start = datetime.datetime.now()

    path = os.path.abspath(os.getcwd())
    toolchain = get_toolchain(path)
    result = toolchain.build(settings, verbose=verbose)

    ts_end = datetime.datetime.now()

    log_command_info(result, ts_start, ts_end)


@app.command()
def run(
        tool: Annotated[
            str,
            typer.Option(
                "--tool", "-t",
                help='Tool to be run',
                autocompletion=complete_run_tool
            )
        ],
        verbose: Annotated[
            bool,
            typer.Option(
                "--verbose", "-v",
                help='Enable verbose output'
            )
        ] = False
):
    '''
    Runs the specified tool, e.g. static code analysis or unit test.
    '''
    ts_start = datetime.datetime.now()

    path = os.path.abspath(os.getcwd())
    toolchain = get_toolchain(path)
    result = toolchain.run(tool, verbose=verbose)

    ts_end = datetime.datetime.now()

    log_command_info(result, ts_start, ts_end)
