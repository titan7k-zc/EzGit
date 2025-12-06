# EzGit

EzGit is a desktop GUI application designed to simplify common Git and file management tasks. Built with Python and the CustomTkinter library, it provides an intuitive, three-panel interface for navigating your file system, managing Git branches, and executing version control commands without leaving the application.

## Features

*   **Integrated File Manager:** Navigate your directory structure, create folders, and rename or delete items directly within the app.
*   **Full Git Lifecycle Support:** Initialize new repositories, clone remote ones, and check the status of your working directory.
*   **Visual Branch Management:** View local and remote branches at a glance. Easily create, switch, and manage branches.
*   **Selective Staging:** Use checkboxes to select specific files to stage, unstage, or discard changes.
*   **Simplified Committing:** Write commit messages and commit your staged changes with a single click.
*   **Effortless Remote Operations:** Push, pull, and fetch changes to/from your remote repository.
*   **In-App Configuration:** Set your Git user name, email, and repository remote URL directly from the UI.
*   **Real-time Command Output:** See the output of every Git command you run in an integrated terminal view.

## UI Layout

The application is organized into a clean three-column layout for a streamlined workflow:

*   **Left Panel (File Manager):** Your file system browser. Navigate directories using the path bar or folder buttons. Select files for Git actions using checkboxes, and perform basic file operations like creating, renaming, and deleting.
*   **Center Panel (Operations Hub):** This is your main control center. It features a terminal for command output, fields for global Git configuration, and tabs for `Basic`, `Remote`, and `Advanced` Git actions.
*   **Right Panel (Branch Manager):** A dedicated space to view and manage all your local and remote branches. Create new branches and switch between existing ones with ease.

## Installation and Setup

To run EzGit on your local machine, follow these steps:

1.  **Prerequisites:** Ensure you have Python and Git installed on your system.
2.  **Clone the Repository:**
    ```sh
    git clone https://github.com/titan7k-zc/EzGit.git
    cd EzGit
    ```
3.  **Install Dependencies:** EzGit relies on the `customtkinter` library. Install it using pip:
    ```sh
    pip install customtkinter
    ```

## Usage

1.  **Launch the Application:**
    ```sh
    python main.pyw
    ```
    *Note: On Windows, the application will automatically request administrator privileges to ensure it has the necessary permissions for file system and Git operations.*

2.  **Navigate:** The application starts in the directory it was launched from. Use the file manager on the left to navigate to your project folder.

3.  **Initialize or Clone:**
    *   If the directory is already a Git repository, the branch manager and config fields will automatically populate.
    *   To start a new repository, click **Initialize Repo**.
    *   To work on an existing remote project, enter its URL in the "Repo URL" field and click **Clone from URL**.

4.  **Perform Git Actions:**
    *   Use the checkboxes next to files to select them for an operation.
    *   Use the buttons in the center panel to perform actions like **Stage Selected**, **Commit**, and **Push**.
    *   Manage branches using the controls in the right-hand panel.
    *   All command outputs are printed to the terminal view at the top of the center panel for immediate feedback.