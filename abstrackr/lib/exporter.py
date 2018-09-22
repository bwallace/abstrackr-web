from xmlbuilder import XmlBuilder
from risbuilder import RisBuilder
from csvbuilder import CsvBuilder

class Exporter:
    def __init__(self, id=0, file_type='ris'):
        self.id = id
        self.file_type = file_type
        # are we going to have filters?
        """
        "fields" is an array that holds which fields do we want to include in
        the export.

        "filter" is a function that takes a label and returns "False" if it
        should not be included in the export.
        """
        self.fields = []
        self.filter = lambda label: True

    def create_export(self):
        if self.file_type not in ['ris-citations', 'ris-labels', 'xml', 'csv', 'excel', 'endnote']:
            raise ValueError('unknown export file_type')


        if self.file_type == "xml":
            xml_tree = XmlBuilder(self.id, self.filter)
            return xml_tree.write_labels()
        elif self.file_type == "ris-citations":
            xml_tree = XmlBuilder(self.id, self.filter)
            ris_builder = RisBuilder(xml_tree.root)
            return ris_builder.write_citations()
        elif self.file_type == "ris-labels":
            xml_tree = XmlBuilder(self.id, self.filter)
            ris_builder = RisBuilder(xml_tree.root)
            return ris_builder.write_labels()
        elif self.file_type == "csv":
            csv_builder = CsvBuilder(self.id, False)
            csv_builder.set_fields(self.fields)
            csv_builder.set_filter(self.filter)
            return csv_builder.write_labels()

    def set_id(self,id):
        self.id = id

    def set_type(self, file_type):
        self.file_type = file_type

    def set_fields(self, new_fields):
        self.fields = new_fields

    def set_filter(self, new_filter):
        self.filter = new_filter

#exporter = Exporter(8181, 'ris')
#exporter.create_export()
