# MAIRA-2 CXR Report Generator v2

This project is a React-based application built with Vite that leverages a backend API (http://127.0.0.1:8000/generate_report/) to generate findings reports from chest X-ray (CXR) images. It provides a user-friendly interface to input image URLs, indications, comparison data, and technique information, and then displays generated findings along with the images.

## Features

*   **Image Input:** Accepts Frontal and Lateral CXR image URLs.
*   **Metadata Input:** Allows users to input indication, comparison, and technique details.
*   **Report Generation:** Communicates with a backend API to generate a findings report.
*   **Image Display:** Displays the uploaded frontal and lateral images.
*   **Findings Report:** Presents the generated findings report in a readable format.
*   **Dark Mode:** Offers a toggleable dark mode for improved user experience.
*   **Cookie Persistence:** Remembers the user's dark mode preference using cookies.
*   **Loading Indicator:** Informs the user when the report is being generated.
*   **Error Handling:** Displays error messages if something goes wrong.
*   **Warning Message:** Provides a warning message indicating that report generation might take some time.

## Technologies Used

*   **React:** A JavaScript library for building user interfaces.
*   **Vite:** A build tool that provides a fast and optimized development experience.
*   **js-cookie:** A simple and lightweight JavaScript API for handling cookies.
*   **CSS Modules:** For styling the application with a modular approach.

## Prerequisites

*   **Node.js:** (version X or higher)  Check with `node -v`
*   **npm:** (usually installed with Node.js)  Check with `npm -v`

## Installation

1.  **Clone the repository:**

    ```bash
    git clone [your-repository-url]
    cd [your-project-directory]
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    # or
    yarn install
    ```

## Running the Application

1.  **Start the development server:**

    ```bash
    npm run dev
    # or
    yarn dev
    ```

    This command will start the Vite development server, and the application will be accessible at a specified local address (usually `http://localhost:5173/`).

## Configuration

*   **API Endpoint:** The application currently communicates with the API endpoint `http://127.0.0.1:8000/generate_report/`.  This is hardcoded in the `App.jsx` file. If you need to change it, you'll need to modify the `fetch` call within the `handleSubmit` function.  Ideally, this should be moved to an environment variable.

## Cookie Usage

This application uses a cookie named `darkMode` to persist the user's dark mode preference across sessions.  The `sameSite` attribute is set to `Lax` to enhance security and comply with modern browser policies.

##  Potential improvements.

*   **Replace hardcoded IP Address with environment variable**:  Use environment variable to configure the API Endpoint so it is not hardcoded and easier to change.
*   **Implement Accessibility best practices**:  Test it with accessibility best practices.
*    **Improve the style of the page:** Apply a style better.

## Contributing

Contributions are welcome!  Feel free to submit pull requests with improvements or bug fixes.
