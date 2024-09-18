import xml.etree.ElementTree as ET
import csv
import argparse

def flatten_xml(xml_file, output_file, common_fields, unique_fields):
    """
    Flattens the XML structure and extracts specific fields to a CSV file.

    Args:
        xml_file (str): Path to the input XML file.
        output_file (str): Path to the output CSV file.
        common_fields (list): List of field names to extract that are common to multiple unique fields.
        unique_fields (list): List of field names to extract that are unique at the lowest level.
    """

    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Create the header row
        header = common_fields + unique_fields
        csv_writer.writerow(header)

        for packet in root.findall('packet'):
            # Extract common field values only once per packet
            common_values = []
            for field_name in common_fields:
                field = packet.find(f'.//field[@name="{field_name}"]')
                common_values.append(field.get('show') if field is not None else '')

            # Recursively find all 'field' elements within the packet
            for field_element in packet.findall('.//field'): 
                row = common_values.copy()  # Start with common values
                for field_name in unique_fields:
                    field = field_element.find(f'./field[@name="{field_name}"]')
                    row.append(field.get('show') if field is not None else '')
                if any(row[len(common_values):]):  # Check if any unique fields were found
                    csv_writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Flatten XML to CSV')
    parser.add_argument('input_file', type=str, help='Path to the input XML file')
    parser.add_argument('output_file', type=str, help='Path to the output CSV file')
    
    # Use a custom function to parse comma-separated lists
    parser.add_argument('--common_fields', type=lambda s: s.split(','), required=True,
                        help='Comma-separated list of common fields (e.g., frame.time,frame.number)')
    parser.add_argument('--unique_fields', type=lambda s: s.split(','), required=True,
                        help='Comma-separated list of unique fields (e.g., cme.futures.mdp3.sbe.v1.5.mdentrypx,cme.futures.mdp3.sbe.v1.5.mdentrysize)')
    args = parser.parse_args()

    # Now args.common_fields and args.unique_fields will be lists
    flatten_xml(args.input_file, args.output_file, args.common_fields, args.unique_fields)