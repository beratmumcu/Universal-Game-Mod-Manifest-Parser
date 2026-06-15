# universal-game-mod-manifest-parser

A lightweight, zero-dependency Python library to parse generic, schema-mappable XML mod manifest and metadata configuration files.

Designed to be completely self-contained, customizable, and clean, making it perfect for custom launchers, multi-game mod managers, web crawlers, or developer automation scripts.

## Origin & Background

This library was originally designed and built as a core module for a *Mount & Blade II: Bannerlord* mod manager, where it was extensively tested on real-world mod configuration files (`SubModule.xml`). 

While it has since been completely generalized to support customizable XML schema mappings for other games and general software configurations, it retains 100% compatibility and robust performance for parsing Bannerlord mod files out-of-the-box.

## Features

- **Schema Mapping**: Define tag-to-key mapping models dynamically to match any custom XML schema.
- **Inner Text & Attribute Parsing**: Pull values from element inner text or attributes (e.g. `<Version value="1.0.0"/>`).
- **Data Type Casting**: Automatically cast parsed values into standard formats (`bool`, `int`).
- **Nested List Resolution**: Extract repeating elements and nested dependencies (e.g. required libraries or mod modules).
- **Zero External Dependencies**: Implemented strictly using Python's built-in standard libraries (`xml.etree.ElementTree`, `os`).

## Installation

Install using pip:
```bash
pip install universal-game-mod-manifest-parser
```
*(Or copy the `universal_game_mod_manifest_parser` source folder directly into your project)*

## Usage

### 1. Basic Metadata Parsing (Default Mapping)

By default, the parser looks for standard tags like `Id`, `Name`, `Version`, `Description`, `Author`, and `Url`.

```python
from universal_game_mod_manifest_parser import parse_xml_manifest

# Searches the folder for standard manifest names (manifest.xml, SubModule.xml, etc.) 
# and parses using default mapping rules.
meta = parse_xml_manifest("C:/MyMods/CoolMod")

print("Mod ID:", meta["id"])
print("Mod Version:", meta["version"])
```

### 2. Advanced Mapping (Custom Schema)

You can customize how tags are mapped, attributes are parsed, and how nested lists are resolved.

#### Example XML Manifest (`custom_manifest.xml`):
```xml
<ModInfo>
  <Identifier value="MyMod123"/>
  <ReleaseVersion>v2.5.1</ReleaseVersion>
  <ProjectURL>https://github.com/example/mymod</ProjectURL>
  <Requirements>
    <Dependency Id="Harmony" Optional="false" MinVersion="v2.2.0"/>
    <Dependency Id="ButterLib" Optional="true"/>
  </Requirements>
</ModInfo>
```

#### Python Parsing Code:
```python
from universal_game_mod_manifest_parser import parse_xml_manifest

# Define custom mappings
custom_mapping = {
    "id": {"tag": "Identifier", "attr": "value"},
    "version": {"tag": "ReleaseVersion"},  # Defaults to inner text
    "website": {"tag": "ProjectURL"}
}

# Define custom list parsers
custom_lists = {
    "dependencies": {
        "parent_tag": "Requirements",
        "item_tag": "Dependency",
        "item_mapping": {
            "id": {"tag": ".", "attr": "Id"},
            "optional": {"tag": ".", "attr": "Optional", "type": "bool"},
            "min_version": {"tag": ".", "attr": "MinVersion"}
        }
    }
}

meta = parse_xml_manifest(
    "custom_manifest.xml", 
    mapping=custom_mapping, 
    lists=custom_lists
)

print("ID:", meta["id"])            # Output: "MyMod123"
print("Version:", meta["version"])  # Output: "v2.5.1"
print("Dependencies:")
for dep in meta["dependencies"]:
    opt = " (Optional)" if dep["optional"] else ""
    print(f"  - {dep['id']}{opt}")  # Output: Harmony, ButterLib (Optional)
```

### 3. Emulating Mount & Blade II: Bannerlord `SubModule.xml` Parser

To parse Bannerlord mod files, map elements as follows:

```python
from universal_game_mod_manifest_parser import parse_xml_manifest

bannerlord_mapping = {
    "id": {"tag": "Id", "attr": "value"},
    "version": {"tag": "Version", "attr": "value"},
    "nexus_id": {"tag": "NexusKey"}
}

bannerlord_lists = {
    "depended_modules": {
        "parent_tag": "DependedModules",
        "item_tag": "DependedModule",
        "item_mapping": {
            "id": {"tag": ".", "attr": "Id"},
            "optional": {"tag": ".", "attr": "Optional", "type": "bool"},
            "dependent_version": {"tag": ".", "attr": "DependentVersion"}
        }
    }
}

mod_data = parse_xml_manifest(
    "C:/Path/To/Bannerlord/Modules/Native",
    mapping=bannerlord_mapping,
    lists=bannerlord_lists
)
```

## Running Tests

Run the test suite using Python's built-in test runner:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

## License

This project is licensed under the MIT License.
