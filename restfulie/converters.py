import json
from xml.etree import ElementTree
from opensearch import OpenSearchDescription
from links import Link, Links

class Converters:

    types = {}

    @staticmethod
    def register(a_type, converter):
        Converters.types[a_type] = converter

    @staticmethod
    def marshaller_for(a_type):
        return Converters.types.get(a_type) or XmlConverter()


class JsonConverter:
    def marshal(self, content):
        return json.dumps(content)

    def unmarshal(self, json_content):
        return _dict2obj(json.loads(json_content))


class _dict2obj(object):
    #from: http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    def __init__(self, dict_):
        for key, value in dict_.items():
            if isinstance(value, (list, tuple)):
               setattr(self, key, [_dict2obj(x) if isinstance(x, dict) else x for x in value])
            else:
               setattr(self, key, _dict2obj(value) if isinstance(value, dict) else value)


class XmlConverter:
    def marshal(self, content):
        return ElementTree.tostring(self._dict_to_etree(content))

    def _dict_to_etree(self, content):
        for key, value in content.items():
            tree = ElementTree.Element(key)
            if type(value) == dict:
                tree.append(self._dict_to_etree(value))
            else:
                tree.text = value
            return tree

    def unmarshal(self, content):
        'Returns an ElementTree Enhanced'
        e = ElementTree.fromstring(content)
        for element in e.getiterator():
            for child in list(element):
                print child.tag, element, list(element), len(element.findall(child.tag)), len(element.findall(child.tag)) == 1
                if len(list(element)) == 0:
                    setattr(element, child.tag, child.text)
                elif len(element.findall(child.tag)) == 1:
                    setattr(element, child.tag, element.find(child.tag))
                else:
                    setattr(element, child.tag, element.findall(child.tag))

        l = []

        for element in e.getiterator("link"):
            d = { 'href': element.attrib['href'],
                  'rel': element.attrib['rel'],
                  'type': element.attrib['type'] }

            l.append(d)

        e.links = lambda: Links(l)
        e.link = lambda x: e.links().get(x)
        return e


class OpenSearchConverter:
    def marshal(self, content):
        return XmlConverter().marshal(content)

    def unmarshal(self, content):
        e_tree = ElementTree.fromstring(content)
        return OpenSearchDescription(e_tree)


class PlainConverter:
    def marshal(self, content):
        return content

    def unmarshal(self, content):
        return content

Converters.register('application/xml', XmlConverter())
Converters.register('text/xml', XmlConverter())
Converters.register('xml', XmlConverter())
Converters.register('text/plain', PlainConverter())
Converters.register('text/json', JsonConverter())
Converters.register('application/json', JsonConverter())
Converters.register('json', JsonConverter())
Converters.register('application/opensearchdescription+xml', OpenSearchConverter())
