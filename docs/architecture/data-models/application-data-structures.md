placeholder for content related to:
* the use of Pydantic data models to represent data structures throughout the application
* Strong preference for Pydantic to the exclusion of Python @dataclass objects (except in rare cases)
* Inheritence from `KPATBaseModel`
* Use of Pydantic data validation to ensure data is correct as early as possible, especially  the path validation, file extension validation, and input sanitization patterns