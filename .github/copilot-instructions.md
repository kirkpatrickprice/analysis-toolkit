This project uses Pydantic for all data models and data validation.

Unless there's specific reason not to, data models should inherit from `src.kp_analysis_toolkit.models.base.KPATBaseModel`.  This model inherits from `pydantic.BaseModel` and common settings required for other models.  

All models should be defined in `src/kp_analysis_toolkit/models/`.  If a model is specific to a particular module, it can be defined in that module's subdirectory, but it should still inherit from `KPATBaseModel`.

All data models should be annotated with type hints, and all fields should have default values or be required.  Use Pydantic's `Field` for additional metadata like descriptions or validation constraints.

All provided input should be validated using Pydantic's validation features. This includes checking types, required fields, and any custom validation logic that may be necessary.

Each toolkit will export its results into Excel.  Excel handling will be provided by Pandas using openpyxl as the engine.