# Maira Project Report Generator

**Maira Project Report Generator** is an asynchronous, object‑oriented FastAPI application that leverages the MAIRA‑2 model from Microsoft (via Hugging Face) to generate detailed chest X‑ray reports. Designed with object‑oriented principles and adhering to PEP 8 guidelines, this project offers efficient image processing, caching, and asynchronous report generation.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides an API to generate chest X‑ray reports using the state‑of‑the‑art MAIRA‑2 model. It downloads and processes X‑ray images asynchronously, formats them for model inference, and generates detailed reports. The implementation makes use of caching to avoid redundant processing and employs modern Python asynchronous features for optimal performance.

## Project Structure

```plaintext
back/
├── __init__.py
├── api.py             # FastAPI application and endpoints
├── config.py          # Configuration settings and environment variables
└── core/
    ├── __init__.py
    ├── image_utils.py # Image processing utilities (download and base64 conversion)
    ├── model_loader.py  # Model loading logic (MAIRA‑2 from Hugging Face)
    └── report_generator.py  # Report generation, caching, and asynchronous processing
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/mvdiogoce/maira_report_generator.git
   cd maira_report_generator
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   Ensure you have a `requirements.txt` that includes necessary packages such as `fastapi`, `uvicorn`, `httpx`, `python-dotenv`, `torch`, `transformers`, and `pillow`. Then run:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Environment Variables:**

   Create a `.env` file in the root directory with the following variables:

   ```env
   HF_TOKEN=your_huggingface_token_here
   ```

2. **Application Configuration:**

   The `config.py` file loads these environment variables and configures thread usage based on whether CUDA is available.

## Usage

To start the FastAPI server, run the following command:

```bash
python api.py
```

The server will be accessible at [http://yourip:8000](http://yourip:8000).

## API Endpoints

- **Generate Report:**  
  `POST /generate_report/`  
  **Form Data Parameters:**
  - `frontal_url` (str): URL for the frontal X‑ray image.
  - `lateral_url` (str): URL for the lateral X‑ray image.
  - `indication` (str): Indication for the report.
  - `comparison` (str): Comparison details.
  - `technique` (str): Imaging technique used.

- **Test Endpoint:**  
  `GET /test`  
  Returns a message confirming the backend is reachable.

- **Root Endpoint:**  
  `GET /`  
  Provides basic information about the API usage.

## Development

- **Coding Standards:**  
  The project is developed using object‑oriented principles and follows PEP 8 standards to ensure code readability and maintainability.
  
- **Logging:**  
  Python’s logging module is used throughout the project for improved debugging and runtime diagnostics.
  
- **Asynchronous Processing:**  
  Asynchronous features in Python (e.g., `asyncio`) are utilized to efficiently handle I/O-bound operations such as image downloads and model inference.

## Contributing

Contributions are welcome! If you would like to propose improvements or fix bugs, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Commit your changes with a clear message:
   ```bash
   git commit -m "Add feature: Description of your feature"
   ```
4. Push the branch to your fork:
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a pull request with a description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Happy Reporting!