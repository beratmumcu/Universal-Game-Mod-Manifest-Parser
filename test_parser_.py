import os
import unittest
import tempfile
import shutil
import xml.etree.ElementTree as ET
from universal_game_mod_manifest_parser.parser import parse_xml_manifest

class TestUniversalManifestParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_default_mapping(self):
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<Manifest>
  <Id value="default-id"/>
  <Name>Default Name</Name>
  <Version value="v1.0.0"/>
  <Author>Berat</Author>
  <Description>A default description</Description>
  <Url>https://example.com</Url>
</Manifest>"""
        
        xml_path = os.path.join(self.test_dir, "manifest.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        data = parse_xml_manifest(self.test_dir)
        self.assertEqual(data["id"], "default-id")
        self.assertEqual(data["name"], "Default Name")
        self.assertEqual(data["version"], "v1.0.0")
        self.assertEqual(data["author"], "Berat")
        self.assertEqual(data["description"], "A default description")
        self.assertEqual(data["url"], "https://example.com")

    def test_custom_mapping_and_types(self):
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<Settings>
  <ModName value="CustomName"/>
  <BuildNumber>42</BuildNumber>
  <IsBeta>true</IsBeta>
</Settings>"""
        
        xml_path = os.path.join(self.test_dir, "metadata.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        custom_mapping = {
            "name": {"tag": "ModName", "attr": "value"},
            "build": {"tag": "BuildNumber", "type": "int"},
            "beta": {"tag": "IsBeta", "type": "bool"}
        }

        data = parse_xml_manifest(self.test_dir, mapping=custom_mapping)
        self.assertEqual(data["name"], "CustomName")
        self.assertEqual(data["build"], 42)
        self.assertTrue(data["beta"])

    def test_nested_lists(self):
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<ModInfo>
  <Dependencies>
    <Dep Id="native" Optional="false"/>
    <Dep Id="harmony" Optional="true"/>
  </Dependencies>
</ModInfo>"""
        
        xml_path = os.path.join(self.test_dir, "module.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        custom_lists = {
            "deps": {
                "parent_tag": "Dependencies",
                "item_tag": "Dep",
                "item_mapping": {
                    "id": {"tag": ".", "attr": "Id"},
                    "optional": {"tag": ".", "attr": "Optional", "type": "bool"}
                }
            }
        }

        data = parse_xml_manifest(self.test_dir, mapping={}, lists=custom_lists)
        deps = data["deps"]
        self.assertEqual(len(deps), 2)
        self.assertEqual(deps[0]["id"], "native")
        self.assertFalse(deps[0]["optional"])
        self.assertEqual(deps[1]["id"], "harmony")
        self.assertTrue(deps[1]["optional"])

    def test_bannerlord_compatibility(self):
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<Module>
  <Id value="Bannerlord.Harmony"/>
  <Version value="v2.4.2"/>
  <NexusKey value="2006"/>
  <DependedModules>
    <DependedModule Id="Native" Optional="false" DependentVersion="v1.4.6"/>
  </DependedModules>
</Module>"""
        
        xml_path = os.path.join(self.test_dir, "SubModule.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

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

        data = parse_xml_manifest(self.test_dir, mapping=bannerlord_mapping, lists=bannerlord_lists)
        self.assertEqual(data["id"], "Bannerlord.Harmony")
        self.assertEqual(data["version"], "v2.4.2")
        self.assertEqual(data["nexus_id"], "2006")
        
        deps = data["depended_modules"]
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0]["id"], "Native")
        self.assertFalse(deps[0]["optional"])
        self.assertEqual(deps[0]["dependent_version"], "v1.4.6")

    def test_missing_and_malformed(self):
        with self.assertRaises(FileNotFoundError):
            parse_xml_manifest(self.test_dir)

        xml_path = os.path.join(self.test_dir, "manifest.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write("<Malformed>Missing end tag")
        with self.assertRaises(ET.ParseError):
            parse_xml_manifest(self.test_dir)

if __name__ == '__main__':
    unittest.main()
