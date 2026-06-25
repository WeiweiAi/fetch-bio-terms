# fetch-bio-terms

Python utilities for retrieving biological terms from ontologies (via BioPortal) and protein databases (via UniProt). 

## Prerequisites

To query ontologies like GO, UBERON, SBO, or CL, you must have a BioPortal API key. The application uses `python-dotenv` to securely load this key.

1. Create a free account at [BioPortal](https://bioportal.bioontology.org).
2. Create a `.env` file in your project `./fetch_bio` and add your key:
```env
BIO_PORTAL_API_KEY=your_actual_api_key_here
```
*If you do not set this variable, the package will explicitly prompt you with an error to set it before making API calls.*

## Installation

This project is built using Hatchling and requires Python 3.12 or higher. 

**Using `uv` (Recommended):**
```bash
uv add git+https://github.com/WeiweiAi/fetch-bio-terms.git
```
or 
```bash
uv tool install git+https://github.com/WeiweiAi/fetch-bio-terms.git
```

**Using `pip`:**
```bash
pip install git+https://github.com/WeiweiAi/fetch-bio-terms.git.
```

## Usage

### Command Line Interface (CLI)

Installing the package automatically registers the `fetch_bio` CLI tool. For the best experience, install it via `uv tool install` to make the `fetch_bio` command available globally in any terminal window. This lets you run `fetch_bio` on its own, without `uv run`.

**Basic Usage:**
```bash
uv run fetch_bio "CL:0000540"
```

**CLI Options:**
The CLI accepts the following optional arguments:
* `-o <file_path>`: Specify an output JSON file path (If omitted, results are not saved to disk.).
* `-q`: Suppress printing the result to the console.

**Example saving output to a specific JSON file:**
```bash
uv run fetch_bio "GO:0055056" -o my_results.json
```

### Python API

You can easily import the core functions into your own Python scripts. 

```python
from fetch_bio import get_bio_info, get_bio_info_batch

# 1. Fetch a single term (dynamically routes to UniProt or BioPortal)
neuron_info = get_bio_info("CL:0000540")
print(neuron_info)

# 2. Fetch from a UniProt URI
protein_info = get_bio_info("http://purl.uniprot.org/uniprot/P11168")
print(protein_info)

# 3. Fetch a batch of URIs and save to a JSON file
uris = ["GO:0055056", "UBERON:0000955", "SBO:0000014"]
batch_results = get_bio_info_batch(uris, json_output="batch_results.json")
```

## Project Structure
* `__init__.py`: Exposes core functions `query_bioportal`, `query_uniprot`, `get_bio_info`, and `get_bio_info_batch`.
* `__main__.py`: Handles the CLI argument parsing and execution.
* `fetch_bio_terms.py`: Contains the core logic, error handling, and API integration.

## License
This project is licensed under the Apache-2.0 License.