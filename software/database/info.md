# Repository Pattern in NovusEdge

The **Repository Pattern** is a design pattern that provides a centralized way to manage data access logic, promoting a clear separation of concerns within the application. In NovusEdge, the repository pattern is implemented to handle interactions with the PostgreSQL database, ensuring that the core business logic remains decoupled from data access details.

## Key Components

### BaseRepository (`base.py`)

- Serves as the foundational class for all specific repositories.
- Provides common CRUD (Create, Read, Update, Delete) operations.
- Utilizes generics to handle different data models.
- Manages database connections through the DatabaseConnection class.

```python

class BaseRepository:
    def add(self, entity: T) -> Optional[int]:
        # Implementation for adding an entity
        pass

    def get_entity(self, **kwargs) -> Optional[T]:
        # Implementation for retrieving a single entity
        pass

    def get_all(self, filters: Optional[Dict[str, Any]] = None, ...) -> List[T]:
        # Implementation for retrieving multiple entities
        pass

    def update(self, entity_id: Union[int, Any], **kwargs) -> bool:
        # Implementation for updating an entity
        pass

    def delete(self, entity_id: Union[int, Any]) -> bool:
        # Implementation for deleting an entity
        pass

```

### GenericRepository (`base.py`)

- Extends BaseRepository to provide generic operations for any table.
- Useful for tables that do not require specialized methods.
- Allows for the creation of universal commands such as -r

```python

class GenericRepository(BaseRepository):
    def __init__(self, db_conn: DatabaseConnection, table_name: str):
        super().__init__(db_conn, table_name=table_name, model=GenericModel)

```

### ShareholderRepository (`shareholder.py`)

- Inherits from BaseRepository to manage operations specific to the SHAREHOLDERS table.
- Implements additional methods like add_shareholder, delete_shareholder, and update_shareholder for - shareholder-specific logic.

```python

class ShareholderRepository(BaseRepository):
    def add_shareholder(self, name: str, ownership: float, investment: float, email: str) -> Optional[int]:
        # Implementation for adding a shareholder
        pass

    def delete_shareholder(self, id: int) -> bool:
        # Implementation for deleting a shareholder
        pass

    def update_shareholder(self, id: int, **kwargs) -> bool:
        # Implementation for updating a shareholder
        pass

```

### Repository Factory (`factory.py`)

- Provides a centralized way to instantiate repositories based on the table name.
- Maintains a mapping (REPOSITORY_MAP) of table names to their corresponding repository classes.
- Raises a RepositoryNotFoundError if a repository for a given table does not exist.

```python

def get_repository(table_name: str, db_conn: DatabaseConnection) -> Type:
    repository_class = REPOSITORY_MAP.get(table_name.upper())
    if repository_class:
        return repository_class(db_conn)
    else:
        raise RepositoryNotFoundError(f"Repository for table '{table_name}' not found.")

```

### Models (`models.py`)

The `models.py` file defines the data structures used within the **NovusEdge** application. Utilizing Python's `dataclasses`, this module provides a clear and concise way to represent the various entities that the application manages. These models serve as the foundation for data manipulation and interaction through the repository pattern.

#### Overview of Models

1. **BaseModel**
    - A flexible base class that provides common functionality to all other models.
    - **Methods:**
        - `to_dict()`: Converts the model instance attributes to a dictionary.
        - `from_dict(data)`: Creates an instance of the model from a dictionary.
        - `__repr__()`: Provides a custom string representation for debugging purposes.

2. **GenericModel**
    - Inherits from [BaseModel](http://_vscodecontentref_/0) and provides a generic structure to handle any table's data.
    - **Attributes:**
        - [id](http://_vscodecontentref_/1): Optional identifier for the record.
        - [__dict__](http://_vscodecontentref_/2): Stores arbitrary key-value pairs representing the table's columns.

3. **ShareholderModel**
    - Represents a shareholder entity within the application.
    - **Attributes:**
        - [id](http://_vscodecontentref_/3): Unique identifier for the shareholder.
        - [name](http://_vscodecontentref_/4): Name of the shareholder.
        - [ownership](http://_vscodecontentref_/5): Percentage of ownership held by the shareholder.
        - [investment](http://_vscodecontentref_/6): Total investment made by the shareholder.
        - [email](http://_vscodecontentref_/7): Contact email of the shareholder.
        - [shareholder_status](http://_vscodecontentref_/8): Current status of the shareholder (e.g., active, inactive).
        - [created_at](http://_vscodecontentref_/9): Timestamp of when the shareholder record was created.

### Benefits of Using the Repository Pattern

- Abstraction: Encapsulates the data access logic, making the rest of the application unaware of the underlying data source.
- Maintainability: Changes to data access logic or the database schema require updates only in the repository classes.
- Testability: Facilitates easier unit testing by allowing repositories to be mocked or stubbed.
- Reusability: Common data operations are centralized, reducing code duplication across the application.
- Separation of Concerns: Keeps business logic separate from data access logic, leading to a cleaner and more organized codebase.

### Workflow in NovusEdge
1. Initialization:

- The NovusEdge class initializes a DatabaseConnection instance.
- Repositories are instantiated using the get_repository factory method based on the table being accessed.

2. Data Operations:

- Services (e.g., adding, updating, deleting shareholders) interact with the repositories to perform database operations.
- Repositories utilize the methods defined in BaseRepository to execute SQL queries and handle transactions.

3. Error Handling:

- The repository pattern centralizes error handling related to data access, ensuring consistent responses to failures.

#### By implementing the repository pattern, NovusEdge achieves a modular and scalable architecture, enhancing the application's robustness and facilitating future enhancements.