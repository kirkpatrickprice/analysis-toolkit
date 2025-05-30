import hashlib
import re  # To handle regular expressions
import sys  # To handle command line arguments and usage
from collections.abc import Generator  # For type hinting
from pathlib import Path  # To handle file paths
from uuid import uuid4  # To generate unique identifiers

from chardet import UniversalDetector  # To detect file encoding

from kp_analysis_toolkit.process_scripts.data_models import (
    LinuxFamilyType,
    ProducerType,
    ProgramConfig,
    Systems,
    SystemType,
)

"""
Version History:
    0.1.0   Initial release
    0.1.1   Colorized the "no results found... deleting file" message in CSV mode
            Corrected the CSV file header line
    0.1.2   2022-11-04
            Fixed CSV export issue with non-printable characters in input files
    0.1.3   2022-11-11
            Added a short-circuit to stop processing files once we've moved beyond the interesting content.  Requires use of a "::" in the regex to identify the section we're looking for
    0.2.0   Rewrite to use OOP -- eases managing data and passing info around
            Export to Excel instad CSV files
            Unique columns whenever field_lists are provided
            Combine results from mulitple lines in the source files into a single row
            Apply filters to exclude systems by specific attributes (e.g. Windows vs Linux, Debian vs RPM, script version, os_version, etc)
    0.2.1   Fixed bug in short-circuit logic that was causing searches to bail out when a comment included the desired pattern
    0.2.2   Better error handling for UnicodeDecodeError message (e.g. when handling UTF-16 files)
    0.2.3   Changes to support building with pyinstaller
    0.2.4   2023-06-25: Fixed unprintable characters bug
    0.3.0   2023-06-30: Added capabilities to process MacOS Auditor result files
    0.3.1   2023-07-03: Added rs_delimiter search config option to handle cases where OS tools don't always print blank values (e.g. MacOS dscl . -readall...)
            See 'audit-macos-users.yaml' for example use case
    0.3.2   2025-01-25: Make changes to support /src layout and Pypi distribution
    0.3.3   2025-02-06: Add Mint as a detected debPattern (common.py)
    0.3.4   2025-02-07: Addressed issue with processing files from Oracle and Kali systems
    0.4.0   2025-05-19: Rewritten as part of the unified kpat CLI
"""


def enumerate_systems_from_source_files(
    program_config: ProgramConfig,
) -> Generator[Systems, None, None]:
    """
    Process the text files to enumerate the systems.

    Args:
        program_config (ProgramConfig): The program configuration object.

    Returns:
        list[Systems]: A list of Systems objects.

    """
    # This function should enumerate the files to process
    # For example, it will read the files in config.source_files
    # and return a list of files to process list of SystemType objects

    for file in get_source_files(
        program_config.source_files_path,
        program_config.source_files_spec,
    ):
        # Process each file and add the results to the list

        encoding: str = get_file_encoding(file)
        producer, producer_version = get_producer_type(file, encoding)
        linux_family: LinuxFamilyType | None = None
        match producer:
            case ProducerType.KPNIXAUDIT:
                system_type: SystemType = SystemType.LINUX
                linux_family = get_linux_family(
                    file=file,
                    encoding=encoding,
                )
            case ProducerType.KPWINAUDIT:
                system_type: SystemType = SystemType.WINDOWS
            case ProducerType.KPMACAUDIT:
                system_type: SystemType = SystemType.DARWIN
            case _:
                system_type: SystemType = SystemType.UNDEFINED
        system_os: str = get_system_os(
            file=file,
            encoding=encoding,
            producer=producer,
        )
        system = Systems(
            system_id=uuid4().hex,
            system_name=file.stem,  # Use the file name (without the extension) as the system name
            file_encoding=encoding,
            system_type=system_type,
            system_os=system_os,
            linux_family=linux_family,
            producer=producer,
            producer_version=producer_version,
            file_hash=generate_file_hash(file),
            file=file.absolute(),
        )
        yield system


def get_config_files(config_path: Path) -> list[Path]:
    """
    Get the list of available configuration files.

    Args:
        config_path (Path): The path to the directory containing configuration files.

    Returns:
        list[Path]: A list of available configuration files as Path objects.

    """
    # This function should return a list of available configuration files

    config_files: list = [config_path / file for file in config_path.glob("*.yaml")]

    return config_files


def get_source_files(start_path: Path, file_spec: str) -> list[Path]:
    """
    Get the list of source files to process.

    Args:
        start_path (str): The starting path to search for files.
        file_spec (str): The file specification to match (e.g. *.txt).

    Returns:
        list[Path]: A list of source files as Path objects.

    """
    # This function should return a list of source files to process
    # For example, it will read the files in the specified directory

    p: Path = Path(start_path).absolute()
    return list(p.rglob(file_spec))


def get_file_encoding(file: Path) -> str:
    """
    Get the file encoding using chardet.

    Args:
        file (Path): The path to the file.

    Returns:
        str: The detected file encoding.

    """
    # This function should detect the file encoding
    # For example, you can use chardet or other libraries to detect the encoding

    detector = UniversalDetector()
    with file.open("rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result["encoding"] if detector.result else "unknown"


def get_linux_family(file: Path, encoding: str) -> LinuxFamilyType | None:
    """
    Get the Linux family type based on the source file.

    Args:
        file (Path): The Path object of the file.
        encoding (str): The file encoding.

    Returns:
        LinuxFamilyType: The Linux family type (e.g. Debian, Redhat, Alpine, etc.) or None if it couldn't be determined.

    """
    # This function should determine the Linux family based on the regular expressions provided below
    # For example, you can use regex or string matching to identify the family

    regex_patterns: dict[str, str] = {
        "deb": r'^System_VersionInformation::/etc/os-release::NAME="(?P<family>Debian|Gentoo|Kali.*|Knoppix|Mint|Raspbian|PopOS|Ubuntu)',
        "rpm": r'^System_VersionInformation::/etc/os-release::NAME="(?P<family>Alma|Amazon|CentOS|ClearOS|Fedora|Mandriva|Oracle|(Red Hat)|Redhat|Rocky|SUSE|openSUSE)',
        "apk": r'^System_VersionInformation::/etc/os-release::NAME="(?P<family>Alpine)',
    }

    with file.open("r", encoding=encoding) as f:
        for line in f:
            for family, pattern in regex_patterns.items():
                regex_result: re.Match[str] | None = re.search(
                    pattern,
                    line,
                    re.IGNORECASE,
                )
                if regex_result:
                    # If a match is found, return the corresponding details
                    return LinuxFamilyType(family)
    # If no match is found, return OTHER
    return LinuxFamilyType.OTHER


def get_system_os(
    file: Path,
    encoding: str,
    producer: ProducerType,
) -> str | None:
    """
    Get the system OS based from the source file.

    Args:
        file (Path): The Path object of the file.
        encoding (str): The file encoding.
        producer (ProducerType): The producer (e.g. KPNIXAudit, KPWinAudit, etc) of the file.
        linux_family (LinuxFamilyType): The Linux family type, if applicable.

    Returns:
        str: The system OS (e.g. Windows 11, Ubuntu 22.04, Redhat 8.6, MacOS 13.4.1) or None if it couldn't be determined.

    """
    # This function should determine the system OS based on the file path and producer type
    # For example, you can use regex or string matching to identify the OS

    match producer:
        case ProducerType.KPWINAUDIT:
            # For Windows systems, extract detailed OS information
            product_name = None
            current_build = None
            ubr = None

            # Define patterns for extracting Windows information
            product_name_pattern = (
                r"^System_OSInfo::ProductName\s*:\s*(?P<product_name>.*)"
            )
            current_build_pattern = r"^System_OSInfo::CurrentBuild\s*:\s*(?P<build>\d+)"
            ubr_pattern = r"^System_OSInfo::UBR\s*:\s*(?P<ubr>\d+)"

            with file.open("r", encoding=encoding) as f:
                for line in f:
                    if not product_name:
                        regex_result = re.search(product_name_pattern, line)
                        if regex_result:
                            product_name = regex_result.group("product_name").strip()

                    if not current_build:
                        regex_result = re.search(current_build_pattern, line)
                        if regex_result:
                            current_build = regex_result.group("build")

                    if not ubr:
                        regex_result = re.search(ubr_pattern, line)
                        if regex_result:
                            ubr = regex_result.group("ubr")

                    # If we have all information, format and return the result
                    if product_name and current_build and ubr:
                        return f"{product_name} (Build {current_build}.{ubr})"
            return None  # If no match is found, return None

        case ProducerType.KPNIXAUDIT:
            # For Linux systems, we can use the /etc/os-release file to determine the OS
            regex_pattern: str = r'^System_VersionInformation::/etc/os-release::PRETTY_NAME="(?P<system_os>.*)"'
            with file.open("r", encoding=encoding) as f:
                for line in f:
                    regex_result: re.Match[str] | None = re.search(
                        regex_pattern,
                        line,
                        re.IGNORECASE,
                    )
                    if regex_result:
                        return regex_result.group("system_os")
            return None

        case ProducerType.KPMACAUDIT:
            # For MacOS systems, extract detailed OS information
            product_name: str | None = None
            product_version: str | None = None
            build_version: str | None = None

            # Define patterns for extracting Windows information
            product_name_pattern = (
                r"^System_VersionInformation::ProductName\s*:\s*(?P<product_name>.*)"
            )
            product_version_pattern = r"^System_VersionInformation::ProductVersion\s*:\s*(?P<product_version>[\d.]+)"
            build_version_pattern = r"^System_VersionInformation::BuildVersion\s*:\s*(?P<build_version>[A-Za-z0-9]+)"

            with file.open("r", encoding=encoding) as f:
                for line in f:
                    if not product_name:
                        regex_result = re.search(product_name_pattern, line)
                        if regex_result:
                            product_name = regex_result.group("product_name").strip()

                    if not product_version:
                        regex_result = re.search(product_version_pattern, line)
                        if regex_result:
                            product_version = regex_result.group(
                                "product_version",
                            ).strip()

                    if not build_version:
                        regex_result = re.search(build_version_pattern, line)
                        if regex_result:
                            build_version = regex_result.group("build_version").strip()

                    # If we have all information, format and return the result
                    if product_name and product_version and build_version:
                        return (
                            f"{product_name} {product_version} (Build {build_version})"
                        )
            return None  # If no match is found, return None

    return None  # If we find an unknown or unmatched producer type


def get_producer_type(file: Path, encoding: str) -> tuple[ProducerType, str]:
    """
    Get the producer type based on the file path.  Uses regular expressions to identify the producer.

    Args:
        file (Path): The path to the file.
        encoding (str): The file encoding.

    Returns:
        ProducerType: The producer type.

    """
    # This function should determine the producer type based on the file path
    # For example, you can use regex or string matching to identify the producer

    """
    Windows: System_PSDetails::KPWINVERSION: 0.4.8
    Linux  : KPNIXVERSION: 0.6.22
    MacOS  : KPMACVERSION: 0.1.0
    """

    regex_patterns: dict[str, str] = {
        "KPNIXAUDIT": r"^(?P<producer_type>KPNIXVERSION): (?P<producer_version>[0-9.]+)",
        "KPWINAUDIT": r"^System_PSDetails::(?P<producer_type>KPWINVERSION): (?P<producer_version>[0-9.]+)",
        "KPMACAUDIT": r"^(?P<producer_type>KPMACVERSION): (?P<producer_version>[0-9.]+)",
    }
    with file.open("r", encoding=encoding) as f:
        for line in f:
            for producer, pattern in regex_patterns.items():
                regex_result: re.Match[str] | None = re.search(
                    pattern,
                    line,
                    re.IGNORECASE,
                )
                if regex_result:
                    # If a match is found, return the corresponding details
                    return (
                        ProducerType(producer),
                        regex_result.group("producer_version"),
                    )
    # If no match is found, return OTHER
    return ProducerType.OTHER


def generate_file_hash(file: Path) -> str:
    """Generate the file hash if not provided."""
    if file is None or not file.exists():
        message: str = f"File path is required to generate the hash {file}."
        raise ValueError(message)

    # Generate the hash (SHA256) of the file
    sha256_hash: hashlib.HASH = hashlib.sha256()
    try:
        with file.open("rb") as f:
            # Read and update hash in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (OSError, PermissionError) as e:
        message: str = f"Error reading file {file}: {e}"
        raise ValueError(message) from e


if __name__ == "__main__":
    print("process_scripts.py should be run as part of the kpat CLI")
    sys.exit(0)
