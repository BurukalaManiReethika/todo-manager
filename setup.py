from setuptools import setup, find_packages
setup(
    name="todo-manager", version="1.0.0",
    description="A CLI task manager in Python",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    entry_points={"console_scripts": ["todo=todo_manager.cli:main"]},
)
