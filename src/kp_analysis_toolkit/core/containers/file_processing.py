"""File processing container for encoding detection, validation, and hashing."""

from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService


def _setup_utils_di_integration(
    file_processing_service: FileProcessingService,
) -> FileProcessingService:
    """Set up DI integration between file processing service and legacy utils."""
    from kp_analysis_toolkit.utils import get_file_encoding, hash_generator

    hash_generator.set_file_processing_service(file_processing_service)
    get_file_encoding.set_file_processing_service(file_processing_service)
    return file_processing_service


class FileProcessingContainer(containers.DeclarativeContainer):
    """File processing and encoding services."""

    # Dependencies
    core = providers.DependenciesContainer()

    # File Processing Components
    encoding_detector: providers.Factory = providers.Factory(
        "kp_analysis_toolkit.core.services.file_processing.encoding.RobustEncodingDetector",
        rich_output=core.rich_output,
    )

    hash_generator: providers.Factory = providers.Factory(
        "kp_analysis_toolkit.core.services.file_processing.hashing.SHA384FileHashGenerator",
    )

    file_validator: providers.Factory = providers.Factory(
        "kp_analysis_toolkit.utils.file_validator.PathLibFileValidator",
    )

    # Main Service with DI integration
    file_processing_service: providers.Factory[FileProcessingService] = (
        providers.Factory(
            _setup_utils_di_integration,
            file_processing_service=providers.Factory(
                FileProcessingService,
                rich_output=core.rich_output,
                encoding_detector=encoding_detector,
                hash_generator=hash_generator,
                file_validator=file_validator,
            ),
        )
    )
