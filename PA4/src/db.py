from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# implement database model classes

# Association table for the many-to-many relationship between Tasks and Categories
association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"))
)


class Task(db.Model):
    """
    Task Model
    Has a one-to-many relationship with the Subtask Model
    Has a many-to-many relationship with the Category Model
    """

    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    description = db.Column(db.String, nullable=True)
    done = db.Column(db.Boolean, nullable=False)
    subtasks = db.relationship("Subtask", cascade="delete")
    categories = db.relationship("Category", secondary=association_table, back_populates="tasks")

    def __init__(self, **kwargs):
        """
        Initialize Task object/entry
        """

        self.description = kwargs.get("description", "")
        self.done = kwargs.get("done", False)

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done,
            "subtasks": [s.serialize() for s in self.subtasks],
            "categories": [c.simpleserialize() for c in self.categories]
        }


class Subtask(db.Model):
    """
    Subtask Model
    Has a one-to-many relationship with the Task Model
    """
    __tablename__ = "subtasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    description = db.Column(db.String, nullable = False)
    done = db.Column(db.Boolean, nullable = False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable = False)

    def __init__(self, **kwargs):
        """
        Initialize Subtask object/entry
        """

        self.description = kwargs.get("description", "")
        self.done = kwargs.get("done", False)
        self.task_id = kwargs.get("task_id",)

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done
        }


class Category(db.Model):
    """
    Category Model
    Has a many-to-many relationship with the Task Model
    """
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    color = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", secondary=association_table, back_populates="categories")

    def __init__(self, **kwargs):
        """
        Initialize Category object/entry
        """
        self.description = kwargs.get("description", "")
        self.color = kwargs.get("color", "")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "color": self.color,
            "tasks": [t.serialize() for t in self.tasks]
        }

    def simple_serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "color": self.color,
        }




class Tag(db.Model):
    """
    Tag Model
    Has a many-to-many relationship with the Task Model
    """
