
SAMPLE_TASKS = [
    (
        "As a user I can log into the application",
        "Implement a login page with email/password form. "
        "Validate credentials against the database. "
        "Return a JWT token on success and handle authentication errors.",
    ),
    (
        "Create an API endpoint to list all tasks in a project",
        "Build a REST GET endpoint at /api/projects/{id}/tasks. "
        "The controller should call the task service which fetches from the repository. "
        "Support filtering by status and pagination.",
    ),
    (
        "Build a dashboard page showing sprint progress",
        "Create a React component that displays a burndown chart and task counts. "
        "Fetch data from the existing API. "
        "Use responsive CSS layout so it works on mobile.",
    ),
    (
        "Add file upload support for task attachments",
        "Allow users to upload files to a task. "
        "Store files securely on the server and save metadata to the database. "
        "Validate file type and size. "
        "Display uploaded attachments in the task detail view.",
    ),
    (
        "Write unit tests for the user service",
        "Add unit test coverage for UserService. "
        "Mock the repository layer and assert business logic behaves correctly. "
        "Cover edge cases for validation and error handling.",
    ),
    (
        "3 - Add Edit Validation (Backend and Frontend)",
        "Relevant AC's - AC3, AC4, AC5, AC6, AC7"
        "- Add all 'Create Task' validation to Editing Task."
        "- Conduct Frontend and Backend testing",
    ),
    (
        "AC2: Error message wrong format",
        """PROBLEM: Given email being
😍😍😍😍😍😍@myemail.com we aren't getting correct error message. Getting "Invalid email or password" instead.

Fix which error message is displayed.
Relevant AC's
- AC3, AC4, AC5, AC6, AC7

- Add all "Create Task" validation to Editing Task.
- Conduct Frontend and Backend testing
"""
    ),
    (
        "The password reset via email API",
        "manual testing if password is correct, testing if password is correct "
        "Implement the existing API from .Net identity library"
    ),
]

