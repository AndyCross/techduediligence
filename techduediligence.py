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


async def fetch_with_retry(session, url, max_retries=5, base_delay=1):
    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except ClientResponseError as e:
            if e.status == 429:  # Too Many Requests
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Rate limited. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                raise
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(base_delay)
    return None


async def get_pypi_info(session, package_name):
    logger.info(f"Fetching PyPI info for package: {package_name}")
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        data = await fetch_with_retry(session, url)
        if not data:
            return None
        info = data['info']
        return {
            'name': info['name'],
            'description': info['summary'],
            'author': info['author'],
            'license': info['license'],
            'project_url': info['project_url'],
            'release_date': data['releases'][info['version']][0]['upload_time']
        }
    except Exception as e:
        logger.error(f"Error processing PyPI info for {package_name}: {str(e)}")
        return None


async def get_nuget_info(session, package_name):
    logger.info(f"Fetching NuGet info for package: {package_name}")
    url = f"https://api.nuget.org/v3/registration5-semver1/{package_name.lower()}/index.json"
    try:
        data = await fetch_with_retry(session, url)
        if not data:
            return None
        latest = data['items'][0]['items'][-1]['catalogEntry']
        return {
            'name': latest['id'],
            'description': latest.get('description', 'N/A'),
            'author': latest.get('authors', 'N/A'),
            'license': latest.get('licenseExpression', 'N/A'),
            'project_url': latest.get('projectUrl', 'N/A'),
            'release_date': latest['published']
        }
    except Exception as e:
        logger.error(f"Error processing NuGet info for {package_name}: {str(e)}")
        return None


async def get_npm_info(session, package_name):
    logger.info(f"Fetching npm info for package: {package_name}")
    url = f"https://registry.npmjs.org/{package_name}"
    try:
        data = await fetch_with_retry(session, url)
        if not data:
            return None
        latest = data['versions'][data['dist-tags']['latest']]
        return {
            'name': data['name'],
            'description': data.get('description', 'N/A'),
            'author': data.get('author', {}).get('name', 'N/A') if isinstance(data.get('author'), dict) else data.get(
                'author', 'N/A'),
            'license': latest.get('license', 'N/A'),
            'project_url': data.get('homepage', 'N/A'),
            'release_date': data.get('time', {}).get(data['dist-tags']['latest'], 'N/A')
        }
    except Exception as e:
        logger.error(f"Error processing npm info for {package_name}: {str(e)}")
        return None


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


def generate_markdown(packages):
    logger.info("Generating Markdown report")
    markdown = "# Tech Due Diligence Report\n\n"
    markdown += "## Open Source Dependencies\n\n"

    for package_type, package_list in packages.items():
        markdown += f"### {package_type} Packages\n\n"
        for package in package_list:
            if package:  # Check if package info is not None
                markdown += f"#### {package['name']}\n\n"
                markdown += f"- Description: {package['description']}\n"
                markdown += f"- Author: {package['author']}\n"
                markdown += f"- License: {package['license']}\n"
                markdown += f"- Project URL: {package['project_url']}\n"
                markdown += f"- Release Date: {package['release_date']}\n\n"

    return markdown


async def fetch_package_info(session, package_type, package_name):
    if package_type == 'PyPI':
        return await get_pypi_info(session, package_name)
    elif package_type == 'NuGet':
        return await get_nuget_info(session, package_name)
    elif package_type == 'npm':
        return await get_npm_info(session, package_name)


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
            'npm': []
        }

        for (package_type, task), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Error processing {package_type} package: {str(result)}")
            elif result:
                processed_packages[package_type].append(result)
            await asyncio.sleep(0.1)  # Small delay between requests

        return processed_packages


async def techduediligence(folder_path):
    logger.info(f"Starting tech due diligence for folder: {folder_path}")
    packages = {
        'PyPI': [],
        'NuGet': [],
        'npm': []
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

    processed_packages = await process_packages(packages)
    markdown = generate_markdown(processed_packages)

    output_file = 'tech_due_diligence_report.md'
    with open(output_file, 'w') as f:
        f.write(markdown)

    logger.info(f"Tech Due Diligence report generated: {output_file}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path to analyze: ")
    asyncio.run(techduediligence(folder_path))