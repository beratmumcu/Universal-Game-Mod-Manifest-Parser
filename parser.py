import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional

DEFAULT_MAPPING = {
    "id": {"tag": "Id", "attr": "value"},
    "name": {"tag": "Name", "attr": "value"},
    "version": {"tag": "Version", "attr": "value"},
    "author": {"tag": "Author", "attr": "value"},
    "description": {"tag": "Description", "attr": "value"},
    "url": {"tag": "Url", "attr": "value"}
}

def parse_xml_manifest(
    file_path: str,
    mapping: Optional[Dict[str, Dict[str, str]]] = None,
    lists: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Parses a generic XML manifest file based on a customizable schema mapping.
    
    Args:
        file_path (str): Path to the XML file or the directory containing it.
            If a directory is passed, it will search for standard manifest names
            like 'manifest.xml', 'metadata.xml', 'SubModule.xml', or 'module.xml'.
        mapping (dict, optional): Maps result keys to XML tag/attribute selectors. E.g.:
            {
                "id": {"tag": "Id", "attr": "value"},
                "version": {"tag": "Version"}  # will fallback to text if attr not specified
            }
        lists (dict, optional): Specifies how to parse list arrays from XML. E.g.:
            {
                "dependencies": {
                    "parent_tag": "DependedModules",
                    "item_tag": "DependedModule",
                    "item_mapping": {
                        "id": {"tag": ".", "attr": "Id"},
                        "optional": {"tag": ".", "attr": "Optional", "type": "bool"}
                    }
                }
            }
            
    Returns:
        dict: Parsed key-value metadata dictionary.
    """
    if os.path.isdir(file_path):
        # Search for common manifest names
        found = False
        for name in ["manifest.xml", "metadata.xml", "SubModule.xml", "module.xml"]:
            p = os.path.join(file_path, name)
            if os.path.exists(p):
                file_path = p
                found = True
                break
        if not found:
            raise FileNotFoundError(f"No standard XML manifest found in directory: {file_path}")
            
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Manifest file not found at: {file_path}")
        
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Use default mapping if none provided
    active_mapping = mapping if mapping is not None else DEFAULT_MAPPING
    result: Dict[str, Any] = {}
    
    def extract_value(elem: ET.Element, selector: Dict[str, str]) -> Any:
        attr_name = selector.get("attr")
        if attr_name:
            val = elem.attrib.get(attr_name)
            if val is not None:
                return val
        else:
            val = elem.attrib.get("value")
            if val is not None:
                return val
        if elem.text:
            return elem.text.strip()
        return None

    # Parse flat values
    for key, selector in active_mapping.items():
        tag = selector.get("tag")
        if not tag:
            continue
        elem = root.find(tag)
        if elem is not None:
            val = extract_value(elem, selector)
            # Parse type if specified
            t_type = selector.get("type")
            if t_type == "bool" and val is not None:
                val = str(val).lower() == "true"
            elif t_type == "int" and val is not None:
                try:
                    val = int(val)
                except ValueError:
                    pass
            result[key] = val
        else:
            result[key] = None
            
    # Parse list elements if specified
    if lists:
        for list_key, list_config in lists.items():
            parent_tag = list_config.get("parent_tag")
            item_tag = list_config.get("item_tag")
            item_mapping = list_config.get("item_mapping", {})
            
            result[list_key] = []
            
            if parent_tag:
                parent_elem = root.find(parent_tag)
                if parent_elem is None:
                    continue
            else:
                parent_elem = root
                
            for item_elem in parent_elem.findall(item_tag):
                item_data = {}
                for ik, selector in item_mapping.items():
                    # Check if the tag is self (meaning attributes/text of the item_elem itself)
                    tag = selector.get("tag")
                    if not tag or tag == "." or tag == item_tag:
                        val = extract_value(item_elem, selector)
                    else:
                        sub_elem = item_elem.find(tag)
                        val = extract_value(sub_elem, selector) if sub_elem is not None else None
                        
                    t_type = selector.get("type")
                    if t_type == "bool" and val is not None:
                        val = str(val).lower() == "true"
                    elif t_type == "int" and val is not None:
                        try:
                            val = int(val)
                        except ValueError:
                            pass
                    item_data[ik] = val
                result[list_key].append(item_data)
                
    return result
