import xml.etree.ElementTree as ET

xml_string = '''<?xml version ="1.0" encoding ="UTF-8"?>

<person>
        <name>Sangmo</name>
        <address>Bhainsepati</address>
</person>
'''

root = ET.fromstring(xml_string)
name = root.find('name').text

print(name)

root.find('address').text = "lalitpur, Bhainsepati"

modified_xml = ET.tostring(root, encoding='unicode')
print(modified_xml)