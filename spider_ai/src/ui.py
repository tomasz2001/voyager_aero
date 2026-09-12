from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.status import Status


console = Console(
    color_system="truecolor"
)



def show_startup_config(
    default_model,
    default_depth,
    default_start_url
):

    console.print()
    console.print(
        Panel(
            "[bold cyan]Spider configuration[/bold cyan]\n\n"
            "[white]Choose the Ollama model and maximum crawl depth.[/white]\n\n"
            "[dim]The next input after this screen will be treated as the search query.[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
    )

    console.print()
    console.print(
        Panel(
            f"[bold white]Model[/bold white]: [cyan]{default_model}[/cyan]\n"
            f"[bold white]Max depth[/bold white]: [cyan]{default_depth}[/cyan]\n"
            f"[bold white]Start URL[/bold white]: [cyan]{default_start_url}[/cyan]",
            border_style="bright_black",
            padding=(1, 2)
        )
    )

    console.print()

    model = console.input(
        "[bold white]Ollama model[/bold white] [dim](default: {default_model})[/dim]: ".format(default_model=default_model)
    ).strip()

    if not model:
        model = default_model

    depth_raw = console.input(
        "[bold white]Max crawl depth[/bold white] [dim](default: {default_depth})[/dim]: ".format(default_depth=default_depth)
    ).strip()

    if not depth_raw:
        depth_raw = str(default_depth)

    try:
        depth = int(depth_raw)
    except ValueError:
        depth = default_depth

    start_url = console.input(
        "[bold white]Start URL[/bold white] [dim](default: {default_start_url})[/dim]: ".format(default_start_url=default_start_url)
    ).strip()

    if not start_url:
        start_url = default_start_url

    return model, max(1, min(depth, 10)), start_url


def clear():

    console.clear()


def show_logo():

    logo_path = Path(__file__).with_name("logo.txt")

    if logo_path.exists():
        logo_art = logo_path.read_text(
            encoding="utf-8"
        ).strip()

        console.print(
            Panel(
                logo_art,
                title="SPIDER AI",
                border_style="bright_black",
                padding=(0, 1)
            )
        )

        return

    console.print(
        Panel(
            "SPIDER AI",
            subtitle="autonomous web search",
            border_style="bright_black",
            padding=(1, 4)
        )
    )


def ask_query():

    console.print()
    console.print(
        Panel(
            "[bold yellow]Use the next command as the search query.[/bold yellow]\n"
            "[dim]Example: spider small cats[/dim]",
            border_style="yellow",
            padding=(1, 2)
        )
    )

    return console.input(
        "[bold white]What are you looking for? [/bold white]"
    ).strip()


def searching(
    message="Searching..."
):

    return Status(
        message,
        spinner="dots",
        spinner_style="cyan"
    )


def status(
    message
):

    console.print(
        f"[dim]•[/dim] {message}",
        highlight=False
    )


def result(
    item
):

    console.print()

    console.print(
        Panel(
            f"[bold white]{item['text']}[/bold white]\n\n"
            f"[cyan]{item['url']}[/cyan]\n\n"
            f"[dim]{item['reason']}[/dim]",
            title="FOUND",
            border_style="cyan",
            padding=(1, 2)
        )
    )


def finished(
    count
):

    console.print()

    if count:

        console.print(
            Panel(
                f"[bold green]"
                f"Search completed."
                f"[/bold green]\n\n"
                f"Results found: "
                f"[bold]{count}[/bold]",
                border_style="green"
            )
        )

    else:

        console.print(
            Panel(
                "[bold yellow]"
                "No matching results found."
                "[/bold yellow]",
                border_style="yellow"
            )
        )


def stopped():

    console.print()

    console.print(
        Panel(
            "[bold yellow]"
            "Search stopped by the user."
            "[/bold yellow]",
            border_style="yellow"
        )
    )
