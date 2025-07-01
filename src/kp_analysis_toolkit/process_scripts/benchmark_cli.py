"""
Benchmarking utilities for the analysis toolkit.

Provides commands to benchmark and compare sequential vs parallel execution performance.
"""

import multiprocessing as mp

import rich_click as click
from rich.console import Console
from rich.table import Table

from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig
from kp_analysis_toolkit.process_scripts.parallel_engine import (
    benchmark_parallel_execution,
    benchmark_sequential_execution,
)
from kp_analysis_toolkit.process_scripts.search_engine import load_search_configs


def _create_results_table(
    sequential_results: dict,
    threaded_results: dict,
    multiprocess_results: dict,
) -> Table:
    """Create a rich table with benchmark results."""
    table = Table(title="Performance Benchmark Results")
    table.add_column("Execution Mode", style="cyan")
    table.add_column("Execution Time (s)", justify="right", style="magenta")
    table.add_column("Total Matches", justify="right", style="green")
    table.add_column("Matches/sec", justify="right", style="yellow")
    table.add_column("Workers", justify="right", style="blue")
    table.add_column("Speedup", justify="right", style="bold green")

    sequential_time = sequential_results["execution_time"]

    table.add_row(
        "Sequential",
        f"{sequential_results['execution_time']:.2f}",
        f"{sequential_results['total_matches']:,}",
        f"{sequential_results['matches_per_second']:.1f}",
        f"{sequential_results['max_workers']}",
        "1.0x",
    )

    threaded_speedup = (
        sequential_time / threaded_results["execution_time"]
        if threaded_results["execution_time"] > 0
        else 0
    )
    table.add_row(
        "Threaded",
        f"{threaded_results['execution_time']:.2f}",
        f"{threaded_results['total_matches']:,}",
        f"{threaded_results['matches_per_second']:.1f}",
        f"{threaded_results['max_workers']}",
        f"{threaded_speedup:.1f}x",
    )

    multiprocess_speedup = (
        sequential_time / multiprocess_results["execution_time"]
        if multiprocess_results["execution_time"] > 0
        else 0
    )
    table.add_row(
        "Multiprocess",
        f"{multiprocess_results['execution_time']:.2f}",
        f"{multiprocess_results['total_matches']:,}",
        f"{multiprocess_results['matches_per_second']:.1f}",
        f"{multiprocess_results['max_workers']}",
        f"{multiprocess_speedup:.1f}x",
    )

    return table


def _determine_best_mode(
    sequential_results: dict,
    threaded_results: dict,
    multiprocess_results: dict,
) -> tuple[str, float]:
    """Determine the best execution mode based on performance."""
    best_mode = "Sequential"
    best_time = sequential_results["execution_time"]

    if threaded_results["execution_time"] < best_time:
        best_mode = "Threaded"
        best_time = threaded_results["execution_time"]

    if multiprocess_results["execution_time"] < best_time:
        best_mode = "Multiprocess"
        best_time = multiprocess_results["execution_time"]

    return best_mode, best_time


@click.command(name="benchmark")
@click.option(
    "audit_config_file",
    "--conf",
    "-c",
    default="audit-all.yaml",
    help="Default: audit-all.yaml. YAML configuration file to use for benchmarking.",
)
@click.option(
    "source_files_path",
    "--start-dir",
    "-d",
    default="./",
    help="Default: current directory. Path to search for files.",
)
@click.option(
    "source_files_spec",
    "--filespec",
    "-f",
    default="*.txt",
    help="Default: *.txt. File specification pattern to match.",
)
@click.option(
    "--max-workers",
    type=int,
    help="Maximum number of workers for parallel execution. Defaults to CPU count.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output.",
)
def benchmark_command(**cli_config: dict) -> None:
    """Benchmark sequential vs parallel execution performance."""
    console = Console()

    try:
        # Create program config for testing
        program_config = ProgramConfig(
            audit_config_file=cli_config["audit_config_file"],
            source_files_path=cli_config["source_files_path"],
            source_files_spec=cli_config["source_files_spec"],
            out_path="benchmark_results/",
            verbose=cli_config.get("verbose", False),
        )

        # Load systems and search configs
        from kp_analysis_toolkit.process_scripts import process_systems

        systems = list(
            process_systems.enumerate_systems_from_source_files(program_config),
        )
        search_configs = load_search_configs(program_config.audit_config_file)

        if not systems:
            console.print("[red]No systems found to benchmark.[/red]")
            return

        if not search_configs:
            console.print("[red]No search configurations found to benchmark.[/red]")
            return

        console.print(
            f"[blue]Benchmarking with {len(systems)} systems and {len(search_configs)} search configs[/blue]",
        )
        console.print(f"[blue]Available CPU cores: {mp.cpu_count()}[/blue]")

        max_workers = cli_config.get("max_workers") or mp.cpu_count()

        # Run benchmarks
        console.print("\n[yellow]Running sequential benchmark...[/yellow]")
        sequential_results = benchmark_sequential_execution(search_configs, systems)

        console.print("[yellow]Running threaded benchmark...[/yellow]")
        threaded_results = benchmark_parallel_execution(
            search_configs,
            systems,
            max_workers,
            use_processes=False,
        )

        console.print("[yellow]Running multiprocess benchmark...[/yellow]")
        multiprocess_results = benchmark_parallel_execution(
            search_configs,
            systems,
            max_workers,
            use_processes=True,
        )

        # Display results
        table = _create_results_table(
            sequential_results,
            threaded_results,
            multiprocess_results,
        )
        console.print(table)

        # Determine and report best mode
        best_mode, best_time = _determine_best_mode(
            sequential_results,
            threaded_results,
            multiprocess_results,
        )
        console.print(f"\n[bold green]Best performance: {best_mode} mode[/bold green]")

        if best_mode != "Sequential":
            sequential_time = sequential_results["execution_time"]
            total_speedup = sequential_time / best_time
            time_saved = sequential_time - best_time
            console.print(f"[green]Total speedup: {total_speedup:.1f}x[/green]")
            console.print(f"[green]Time saved: {time_saved:.2f} seconds[/green]")

    except (ValueError, OSError) as e:
        console.print(f"[red]Error during benchmarking: {e}[/red]")
        if cli_config.get("verbose"):
            import traceback

            console.print(traceback.format_exc())


if __name__ == "__main__":
    benchmark_command()
