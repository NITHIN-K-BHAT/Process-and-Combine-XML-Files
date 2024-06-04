import os
import json
from lxml import etree as ETL

def read_json(filename):
    print("filename : ",filename)
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def find_xml_files(directory):
    xml_files = []
    for root, dirs, files in os.walk(directory):
        print("directory :",directory)    
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    return xml_files
    

def find_tag_data(xml_file, slsdocid):
    print("xml_file :", xml_file)
    tag_data = None
    tag_element = None
    try:
        tree = ETL.parse(xml_file)
        root = tree.getroot()
        for elem in root.iter():
            if 'SLSDOCID' in elem.attrib and elem.attrib['SLSDOCID'] == slsdocid:
                tag_data = ETL.tostring(elem, encoding='unicode')
                print("Found Element:", elem)
                tag_element = elem
                # Print the parent element
                parent_element = elem.getparent()
                if parent_element is not None:
                    print("Parent Element:", parent_element)
                else:
                    print("No parent element found.")
                break
    except ETL.XMLSyntaxError as e:
        print(f"Error parsing XML file {xml_file}: {e}")
    return tag_data, tag_element

def create_dita_file(slsdocid, tag_data, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    filename = os.path.join(output_folder, slsdocid + '.dita')
    with open(filename, 'w') as f:
        f.write(tag_data)
    print("DITA file created:", filename)
    return filename

def update_xml(xml_file, include_path, tag_element):
    xi_ns = {"xi": "http://www.w3.org/2001/XInclude"}
    include_element = ETL.Element("{%s}include" % xi_ns['xi'], attrib={"href": include_path}, nsmap=xi_ns)
    parent = tag_element.getparent()
    parent_index = list(parent).index(tag_element)
    parent.insert(parent_index, include_element)
    parent.remove(tag_element)
    tree = ETL.ElementTree(parent.getroottree().getroot())
    tree.write(xml_file)

def main():
    json_data = read_json('slsdocid.json')
    xml_files = find_xml_files('directory (1)')
    print("xml_file :::",xml_files)
    output_folder = 'XIincludes'
    for item in json_data:
        slsdocid = item['slsdocid']
        # print("slsdocid :",slsdocid)
        for xml_file in xml_files:
            if item['file_name'] == os.path.basename(xml_file):  # Check if the 'file_name' matches the XML file name
                tag_data, tag_element = find_tag_data(xml_file, slsdocid)
                if tag_data:
                    dita_file_path = create_dita_file(slsdocid, tag_data, output_folder)
                    # Update XML
                    update_xml(xml_file, dita_file_path, tag_element)

if __name__ == "__main__":
    main()
