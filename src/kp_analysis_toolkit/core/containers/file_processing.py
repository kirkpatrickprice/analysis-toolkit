from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService


class FileProcessingContainer(containers.DeclarativeContainer):
    """File processing and encoding services."""

    # Dependencies
    core = providers.DependenciesContainer()

    # File Processing Components
    encoding_detector: providers.Factory = providers.Factory(
        "kp_analysis_toolkit.utils.get_file_encoding.ChardetEncodingDetector",
    )

    hash_generator: providers.Factory = providers.Factory(
        "kp_analysis_toolkit.utils.shared_funcs.SHA256HashGenerator",
    )

    file_validator: providers.Factory = providers.Factory(
        "kp_analysis_toolkit.utils.shared_funcs.PathLibFileValidator",
    )

    # Main Service
    file_processing_service: providers.Factory[FileProcessingService] = (
        providers.Factory(
            FileProcessingService,
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=core.rich_output,
        )
    )
