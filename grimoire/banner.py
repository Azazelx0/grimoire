"""GRIMOIRE banner and styled output using Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from grimoire import __version__

console = Console()

BANNER_ART = r"""
   ██████╗ ██████╗ ██╗███╗   ███╗ ██████╗ ██╗██████╗ ███████╗
  ██╔════╝ ██╔══██╗██║████╗ ████║██╔═══██╗██║██╔══██╗██╔════╝
  ██║  ███╗██████╔╝██║██╔████╔██║██║   ██║██║██████╔╝█████╗
  ██║   ██║██╔══██╗██║██║╚██╔╝██║██║   ██║██║██╔══██╗██╔══╝
  ╚██████╔╝██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║██║  ██║███████╗
   ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝"""


def print_banner():
    banner_text = Text(BANNER_ART, style="bold red")
    tagline = Text("\n       Where words are forged into weapons.", style="bold yellow")
    version = Text(f"                         v{__version__}", style="dim")
    full = banner_text + tagline + version

    console.print(Panel(full, border_style="red", padding=(0, 1)))
    console.print()


def success(msg: str):
    console.print(f"  [bold green]✓[/bold green] {msg}")


def error(msg: str):
    console.print(f"  [bold red]✗[/bold red] {msg}")


def warning(msg: str):
    console.print(f"  [bold yellow]![/bold yellow] {msg}")


def info(msg: str):
    console.print(f"  [bold cyan]→[/bold cyan] {msg}")


def dim(msg: str):
    console.print(f"  [dim]{msg}[/dim]")
