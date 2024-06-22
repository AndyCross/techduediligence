import os
import json
import re
import asyncio
import aiohttp
import logging
from datetime import datetime
from xml.etree import ElementTree as ET
from aiohttp import ClientResponseError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ... [Previous fetch_with_retry, get_pypi_info, get_nuget_info, get_npm_info functions remain the same] ...

def parse_requirements_txt(file_path):
    logger.info(f"Parsing requirements.txt file: {file_path}")
    with open(file_path, 'r') as file:
        return [line.strip().split('==')[0] for line in file if line.strip() and not line.startswith('#')]


def parse_csproj(file_path):
    logger.info(f"Parsing .csproj file: {file_path}")
    tree = ET.parse(file_path)
    root = tree.getroot()
    packages = []
    for item_group in root.findall(".//ItemGroup"):
        for package_ref in item_group.findall("PackageReference"):
            packages.append(package_ref.get("Include"))
    return packages


def parse_package_json(file_path):
    logger.info(f"Parsing package.json file: {file_path}")
    with open(file_path, 'r') as file:
        data = json.load(file)
        dependencies = data.get("dependencies", {})
        dev_dependencies = data.get("devDependencies", {})
        return list(dependencies.keys()) + list(dev_dependencies.keys())


def parse_gemfile(file_path):
    logger.info(f"Parsing Gemfile: {file_path}")
    with open(file_path, 'r') as file:
        return [line.split("'")[1] for line in file if line.strip().startswith("gem '")]


def parse_composer_json(file_path):
    logger.info(f"Parsing composer.json file: {file_path}")
    with open(file_path, 'r') as file:
        data = json.load(file)
        return list(data.get("require", {}).keys())


def parse_cargo_toml(file_path):
    logger.info(f"Parsing Cargo.toml file: {file_path}")
    dependencies = []
    with open(file_path, 'r') as file:
        in_dependencies = False
        for line in file:
            if line.strip() == "[dependencies]":
                in_dependencies = True
            elif in_dependencies and line.strip().startswith('['):
                break
            elif in_dependencies and '=' in line:
                package = line.split('=')[0].strip()
                dependencies.append(package)
    return dependencies


async def check_vulnerability(session, package_name, ecosystem):
    url = f"https://api.osv.dev/v1/query"
    data = {
        "package": {
            "name": package_name,
            "ecosystem": ecosystem
        }
    }
    try:
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            result = await response.json()
            return len(result.get("vulns", [])) > 0
    except Exception as e:
        logger.error(f"Error checking vulnerability for {package_name}: {str(e)}")
        return False


def check_license_compatibility(license1, license2):
    compatible_pairs = [
        {"MIT", "Apache-2.0"},
        {"MIT", "BSD-3-Clause"},
        {"Apache-2.0", "BSD-3-Clause"}
    ]
    return {license1, license2} in compatible_pairs


async def fetch_package_info(session, package_type, package_name):
    info = None
    if package_type == 'PyPI':
        info = await get_pypi_info(session, package_name)
    elif package_type == 'NuGet':
        info = await get_nuget_info(session, package_name)
    elif package_type == 'npm':
        info = await get_npm_info(session, package_name)
    # Add handlers for new package types here

    if info:
        info['has_known_vulnerability'] = await check_vulnerability(session, package_name, package_type.lower())

    return info


async def process_packages(packages):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for package_type, package_list in packages.items():
            for package in package_list:
                task = asyncio.ensure_future(fetch_package_info(session, package_type, package))
                tasks.append((package_type, task))

        results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

        processed_packages = {
            'PyPI': [],
            'NuGet': [],
            'npm': [],
            'Ruby': [],
            'PHP': [],
            'Rust': []
        }

        for (package_type, task), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Error processing {package_type} package: {str(result)}")
            elif result:
                processed_packages[package_type].append(result)
            await asyncio.sleep(0.1)  # Small delay between requests

        return processed_packages


def generate_markdown(packages):
    logger.info("Generating Markdown report")
    markdown = "# Tech Due Diligence Report\n\n"
    markdown += "## Open Source Dependencies\n\n"

    for package_type, package_list in packages.items():
        if package_list:
            markdown += f"### {package_type} Packages\n\n"
            for package in package_list:
                if package:  # Check if package info is not None
                    markdown += f"#### {package['name']}\n\n"
                    markdown += f"- Description: {package['description']}\n"
                    markdown += f"- Author: {package['author']}\n"
                    markdown += f"- License: {package['license']}\n"
                    markdown += f"- Project URL: {package['project_url']}\n"
                    markdown += f"- Release Date: {package['release_date']}\n"
                    markdown += f"- Known Vulnerability: {'Yes' if package.get('has_known_vulnerability') else 'No'}\n\n"

    markdown += "\n## License Compatibility\n\n"
    all_licenses = [package['license'] for packages in packages.values() for package in packages if package]
    for i, license1 in enumerate(all_licenses):
        for license2 in all_licenses[i + 1:]:
            markdown += f"- {license1} and {license2}: {'Compatible' if check_license_compatibility(license1, license2) else 'Potentially Incompatible'}\n"

    return markdown


async def techduediligence(folder_path):
    logger.info(f"Starting tech due diligence for folder: {folder_path}")
    packages = {
        'PyPI': [],
        'NuGet': [],
        'npm': [],
        'Ruby': [],
        'PHP': [],
        'Rust': []
    }

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('requirements.txt'):
                logger.info(f"Found requirements.txt: {file_path}")
                packages['PyPI'].extend(parse_requirements_txt(file_path))
            elif file.endswith('.csproj'):
                logger.info(f"Found .csproj file: {file_path}")
                packages['NuGet'].extend(parse_csproj(file_path))
            elif file == 'package.json':
                logger.info(f"Found package.json: {file_path}")
                packages['npm'].extend(parse_package_json(file_path))
            elif file == 'Gemfile':
                logger.info(f"Found Gemfile: {file_path}")
                packages['Ruby'].extend(parse_gemfile(file_path))
            elif file == 'composer.json':
                logger.info(f"Found composer.json: {file_path}")
                packages['PHP'].extend(parse_composer_json(file_path))
            elif file == 'Cargo.toml':
                logger.info(f"Found Cargo.toml: {file_path}")
                packages['Rust'].extend(parse_cargo_toml(file_path))

    processed_packages = await process_packages(packages)
    markdown = generate_markdown(processed_packages)

    output_file = 'tech_due_diligence_report.md'
    with open(output_file, 'w') as f:
        f.write(markdown)

    logger.info(f"Tech Due Diligence report generated: {output_file}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path to analyze: ")
    asyncio.run(techduediligence(folder_path))