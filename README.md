# TechDueDiligence

TechDueDiligence is a powerful, asynchronous Python script designed to automate the process of gathering information about open-source dependencies in your projects. It analyzes different dependency files, fetches package information from public repositories, and generates a comprehensive Markdown report.

## Features

- Supports multiple package ecosystems:
  - Python (pip) via `requirements.txt`
  - .NET (NuGet) via `.csproj` files
  - JavaScript (npm) via `package.json`
- Asynchronous processing for faster results
- Resilient to rate limiting with exponential backoff and retry logic
- Detailed logging for transparency and debugging
- Generates a well-formatted Markdown report

## Installation

1. Ensure you have Python 3.7 or later installed on your system.

2. Clone this repository:
   ```
   git clone https://github.com/andycross/techduediligence.git
   cd techduediligence
   ```

3. (Optional) Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

4. Install the required dependencies:
   ```
   pip install aiohttp
   ```

## Usage

1. Run the script:
   ```
   python techduediligence.py
   ```

2. When prompted, enter the path to the folder you want to analyze:
   ```
   Enter the folder path to analyze: /path/to/your/project
   ```

3. The script will process the folder and generate a `tech_due_diligence_report.md` file in the same directory as the script.

## Output

The generated report includes the following information for each package:

- Name
- Description
- Author
- License
- Project URL
- Release Date

## Customization

You can customize the script by modifying the following aspects:

- Adjust the `max_retries` and `base_delay` parameters in the `fetch_with_retry` function to change the retry behavior.
- Modify the `generate_markdown` function to alter the format of the output report.
- Add support for additional package ecosystems by creating new parsing functions and API calls.

## Contributing

Contributions to TechDueDiligence are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool fetches data from public APIs and should be used responsibly. Be aware of and respect the terms of service for PyPI, NuGet, and npm.

## Acknowledgments

- Thanks to the Python community for the excellent `asyncio` and `aiohttp` libraries.
- Inspired by the need for better open-source dependency management and due diligence in software projects.