import json
import os
import logging
from dotenv import load_dotenv
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch API key securely from environment variables
# if not set, the user will be prompted to set it before making API calls
def get_bio_portal_api_key() -> str:
    # This physically loads the variables from the .env file into your local environment
    load_dotenv()
    api_key = os.getenv("BIO_PORTAL_API_KEY")
    if not api_key:
        raise ValueError("BioPortal API key is missing. Set BIO_PORTAL_API_KEY environment variable.")
    return api_key

BIO_PORTAL_API_KEY = get_bio_portal_api_key()

class BioLookupError(Exception):
    """Custom exception raised for biological entity lookup failures."""
    pass

def get_last_uri_segment(uri: str) -> str:
    """
    Extract the last segment of a URI, converting underscores to colons if present.
    
    This is typically used to extract a biological identifier (like a GO term) 
    from a full URI.

    Args:
        uri (str): The full URI string to parse.

    Returns:
        str: The extracted identifier segment.

    Example:
        >>> get_last_uri_segment("http://purl.obolibrary.org/obo/GO_0055056")
        'GO:0055056'
    """
    return uri.rstrip('/').split('/')[-1].replace('_', ':')

def query_bioportal(term: str, api_key: str = BIO_PORTAL_API_KEY, ontology: Optional[str] = None) -> Dict[str, Any]:
    """
    Query the BioPortal API for a specific biological term.

    Args:
        term (str): The search term or CURIE (e.g., 'GO:0055056').
        api_key (str, optional): The BioPortal API key.
        ontology (str, optional): The specific ontology acronym to restrict the search to.

    Returns:
        Dict[str, Any]: The full JSON response payload.
    """
    if not api_key:
        raise ValueError("BioPortal API key is missing. Set BIO_PORTAL_API_KEY environment variable.")

    url = "https://data.bioontology.org/search"
    params = {"q": term, "require_exact_match": "true"}
    
    # Restrict search to the origin ontology if provided
    if ontology:
        params["ontologies"] = ontology

    headers = {"Authorization": f"apikey token={api_key}"}
    response = requests.get(url, params=params, headers=headers)

    if not response.ok:
        raise BioLookupError(f"BioPortal lookup failed: {response.status_code} {response.reason}")
    
    return response.json()

def get_bioportal_info(curie: str, api_key: str = BIO_PORTAL_API_KEY) -> Dict[str, Any]:
    """
    Retrieve standardized entity information from a given CURIE via BioPortal.

    Args:
        curie (str): The Compact URI (CURIE) of the entity (e.g., 'CHEBI:4167').
        api_key (str, optional): The BioPortal API key. Defaults to the 
            environment variable `BIO_PORTAL_API_KEY`.

    Returns:
        Dict[str, Any]: A dictionary containing 'label', 'definition', 'synonyms', 
        and the BioPortal '@id'.

    Raises:
        ValueError: If no API key is provided.
        BioLookupError: If the API request fails or if no matching term is found in the collection.
    """
    # Extract the origin ontology from the CURIE (e.g., 'UBERON' from 'UBERON:0000955')
    ontology_prefix = curie.split(":")[0] if ":" in curie else None
    
    try:
        # Step 1: Try searching specifically within the origin ontology first
        response = query_bioportal(curie, api_key, ontology=ontology_prefix)
        collection = response.get("collection", [])
        
        # Step 2: If nothing found, fall back to a global search across all ontologies
        if not collection:
            response = query_bioportal(curie, api_key)
            collection = response.get("collection", [])
            
    except (BioLookupError, ValueError) as e:
        logger.error(f"Error fetching BioPortal info: {e}")
        raise

    if not collection:
        raise BioLookupError(f"No match found in BioPortal for CURIE: {curie}")

    # Step 3: Smart filtering to find the most meaningful entry
    best_entry = collection[0]
    for entry in collection:
        label = entry.get("prefLabel", "")
        
        # If the label isn't just the ID itself, this is the definitive match
        if label and label.upper() != curie.upper():
            best_entry = entry
            break

    return {
        "label": best_entry.get("prefLabel", ""),
        "definition": best_entry.get("definition", []),
        "synonyms": best_entry.get("synonym", []),
        "id": best_entry.get("@id", ""),
    }

def query_uniprot(uniprot_id: str) -> Dict[str, Any]:
    """
    Query the UniProt REST API for a specific UniProt ID.

    Args:
        uniprot_id (str): The UniProt identifier (e.g., 'P11168').

    Returns:
        Dict[str, Any]: The full JSON response payload from the UniProt API.

    Raises:
        BioLookupError: If the HTTP request fails or returns a non-200 status code.
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    response = requests.get(url)
    
    if not response.ok:
        raise BioLookupError(f"UniProt lookup failed: {response.status_code} {response.reason}")
    
    return response.json()


def get_uniprot_info(uniprot_id: str) -> Dict[str, Any]:
    """
    Retrieve standardized protein information (name, synonyms, organism) from a UniProt ID.

    Args:
        uniprot_id (str): The UniProt identifier (e.g., 'P11168').

    Returns:
        Dict[str, Any]: A dictionary containing the standard 'label', 'synonyms' list, 
        and 'organism' list.

    Raises:
        BioLookupError: If the underlying UniProt API query fails.
    """
    try:
        response = query_uniprot(uniprot_id)
    except BioLookupError as e:
        logger.error(f"Error fetching UniProt info: {e}")
        raise

    protein_desc = response.get("proteinDescription", {})
    protein_name = protein_desc.get("recommendedName", {}).get("fullName", {}).get("value")
    
    organism_data = response.get("organism", {})
    organism = [
        name for name in [organism_data.get("scientificName"), organism_data.get("commonName")]
        if name  # Filters out None values
    ]
    
    synonyms = protein_desc.get("alternativeNames", [])
    
    return {
        "label": protein_name,
        "synonyms": [syn.get("fullName", {}).get("value") for syn in synonyms if syn.get("fullName", {}).get("value")],
        "organism": organism
    }       

def get_bio_info(uri: str, json_output: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Dynamically fetch biological entity information based on the provided URI.

    This function determines whether to query UniProt or BioPortal based on 
    the presence of 'uniprot' in the URI string.

    Args:
        uri (str): The full URI of the biological entity to look up.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the biological information, 
        or None if the lookup fails.
    """
    try:
        if 'uniprot' in str(uri):
            uniprot_id = get_last_uri_segment(uri).split(":")[-1]
            data_json = get_uniprot_info(uniprot_id)
        else:
            data_json = get_bioportal_info(get_last_uri_segment(uri))
        
        if json_output:
            with open(json_output, "w", encoding="utf-8") as f:
                json.dump(data_json, f, indent=4)        
        return data_json
            
    except BioLookupError as e:
        logger.warning(f"Cannot find biological info for {uri}. Reason: {e}")
        return None

def get_bio_info_batch(uris: list, json_output: Optional[str] = None) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Fetch biological entity information for a batch of URIs.

    Args:
        uris (list): A list of URIs to look up.

    Returns:
        Dict[str, Optional[Dict[str, Any]]]: A dictionary mapping each URI to its corresponding 
        biological information, or None if the lookup fails.
    """
    result = {uri: get_bio_info(uri, json_output) for uri in uris}
    
    if json_output:
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
    return result