# TechDueDiligence

TechDueDiligence is a powerful, asynchronous Python script designed to automate the process of gathering information about open-source dependencies in your projects. It analyzes different dependency files, fetches package information from public repositories, checks for vulnerabilities, assesses license compatibility, and generates a comprehensive Markdown report.

## Features

- Supports multiple package ecosystems:
  - Python (pip) via `requirements.txt`
  - .NET (NuGet) via `.csproj` files
  - JavaScript (npm) via `package.json`
  - Ruby via `Gemfile`
  - PHP via `composer.json`
  - Rust via `Cargo.toml`
- Asynchronous processing for faster results
- Resilient to rate limiting with exponential backoff and retry logic
- Basic security vulnerability check using the OSV (Open Source Vulnerabilities) API
- Simple license compatibility assessment
- Detailed logging for transparency and debugging
- Generates a well-formatted Markdown report

## Installation

1. Ensure you have Python 3.7 or later installed on your system.

2. Clone this repository:
   ```
   git clone https://github.com/yourusername/techduediligence.git
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
- Known Vulnerability Status

Additionally, the report includes a section on license compatibility between the different packages used in the project.

## Roadmap

We're constantly working to improve TechDueDiligence. Here are some features we're planning to implement or enhance:

1. **Support for Additional Ecosystems**: 
   - ✅ Ruby (Gemfile)
   - ✅ PHP (composer.json)
   - ✅ Rust (Cargo.toml)
   - More ecosystems in the future

2. **Security Vulnerability Check**: 
   - ✅ Basic integration with OSV (Open Source Vulnerabilities) API
   - Enhance with more comprehensive vulnerability databases
   - Provide more detailed vulnerability information

3. **License Compatibility Check**: 
   - ✅ Basic license compatibility assessment
   - Enhance with more sophisticated license analysis

4. **Dependency Graph Visualization**: 
   - Create graphical representations of dependency trees
   - Helps understand relationships and potential conflicts

5. **Automated Report Generation**: 
   - Schedule periodic scans
   - Integrate with CI/CD pipelines
   - Send reports via email

6. **Historical Comparison**: 
   - Track changes in dependencies over time
   - Compare current dependencies with past states
   - Identify newly introduced risks

7. **Dependency Health Metrics**: 
   - Number of maintainers
   - Frequency of updates
   - Open issues
   - Assess overall health and reliability of dependencies

We welcome contributions to help implement and improve these features!

## Customization

You can customize the script by modifying the following aspects:

- Adjust the `max_retries` and `base_delay` parameters in the `fetch_with_retry` function to change the retry behavior.
- Modify the `generate_markdown` function to alter the format of the output report.
- Add support for additional package ecosystems by creating new parsing functions and API calls.
- Enhance the `check_license_compatibility` function to include more license types and compatibility rules.

## Contributing

Contributions to TechDueDiligence are welcome! Please feel free to submit a Pull Request, especially for items on our roadmap. If you're planning to work on a major feature, please open an issue first to discuss the implementation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool fetches data from public APIs and should be used responsibly. Be aware of and respect the terms of service for PyPI, NuGet, npm, OSV, and any other package repositories or services you interact with.

## Acknowledgments

- Thanks to the Python community for the excellent `asyncio` and `aiohttp` libraries.
- Inspired by the need for better open-source dependency management and due diligence in software projects.
- Thanks to the OSV (Open Source Vulnerabilities) project for providing a public API for vulnerability data.