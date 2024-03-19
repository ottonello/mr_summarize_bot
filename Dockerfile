# Use python 3.11 base image
FROM python:3.11
# Install poetry
RUN pip install poetry
# Set the working directory
WORKDIR /app
# Copy the poetry.lock and pyproject.toml files
COPY poetry.lock pyproject.toml /app/
# Install the dependencies
RUN poetry install
# Copy the rest of the files
COPY . /app
# Expose the port
EXPOSE 3000

# Run the application
CMD ["poetry", "run", "python", "main.py"]
