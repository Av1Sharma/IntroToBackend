from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# implement database model classes

class Task(db.Model):
    """
    Task Model
    Has a one-to-many relationship with the Subtask Model
    Has a many-to-many relationsjip with the Category Model
    """

    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    description = db.Column(db.String, nullable=True)
    done = db.Column(db.Boolean, nullable=False)

    def __init__(sef, **kwargs):
        """
        Initialize Task object/entry
        """

        self.description = kwargs.get("description", "")
        self.done = kwargs.get("done", False)

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done
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
    task_id = db.Column(db.Integer, db.ForeignKey("tasks_id"), nullable = False)

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


class Tag(db.Model):
    """
    Tag Model
    Has a many-to-many relationship with the Task Model
    """
