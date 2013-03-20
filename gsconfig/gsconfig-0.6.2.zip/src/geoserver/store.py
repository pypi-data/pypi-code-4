import geoserver.workspace as ws
from geoserver.resource import featuretype_from_index, coverage_from_index
from geoserver.support import ResourceInfo, xml_property, key_value_pairs, \
        write_bool, write_dict, write_string, url

def datastore_from_index(catalog, workspace, node):
    name = node.find("name")
    return DataStore(catalog, workspace, name.text)

def coveragestore_from_index(catalog, workspace, node):
    name = node.find("name")
    return CoverageStore(catalog, workspace, name.text)

class DataStore(ResourceInfo):
    resource_type = "dataStore"
    save_method = "PUT"

    def __init__(self, catalog, workspace, name):
        super(DataStore, self).__init__()

        assert isinstance(workspace, ws.Workspace)
        assert isinstance(name, basestring)
        self.catalog = catalog
        self.workspace = workspace
        self.name = name

    @property
    def href(self):
        return url(self.catalog.service_url, 
            ["workspaces", self.workspace.name, "datastores", self.name + ".xml"])

    enabled = xml_property("enabled", lambda x: x.text == "true")
    name = xml_property("name")
    connection_parameters = xml_property("connectionParameters", key_value_pairs)

    writers = dict(enabled = write_bool("enabled"),
                   name = write_string("name"),
                   connectionParameters = write_dict("connectionParameters"))


    def get_resources(self):
        res_url = url(self.catalog.service_url,
            ["workspaces", self.workspace.name, "datastores", self.name, "featuretypes.xml"])
        xml = self.catalog.get_xml(res_url)
        def ft_from_node(node):
            return featuretype_from_index(self.catalog, self.workspace, self, node)

        return [ft_from_node(node) for node in xml.findall("featureType")]

class UnsavedDataStore(DataStore):
    save_method = "POST"

    def __init__(self, catalog, name, workspace):
        super(UnsavedDataStore, self).__init__(catalog, workspace, name)
        self.dirty.update(dict(
            name=name, enabled=True, connectionParameters=dict()))

    @property
    def href(self):
        path = [ "workspaces",
                 self.workspace.name, "datastores"]
        query = dict(name=self.name)
        return url(self.catalog.service_url, path, query)

class CoverageStore(ResourceInfo):
    resource_type = 'coverageStore'
    save_method = "PUT"

    def __init__(self, catalog, workspace, name):
        super(CoverageStore, self).__init__()

        assert isinstance(workspace, ws.Workspace)
        assert isinstance(name, basestring)

        self.catalog = catalog
        self.workspace = workspace
        self.name = name

    @property
    def href(self):
        return url(self.catalog.service_url,
            ["workspaces", self.workspace.name, "coveragestores", self.name + ".xml"])

    enabled = xml_property("enabled", lambda x: x.text == "true")
    name = xml_property("name")
    url = xml_property("url")
    type = xml_property("type")

    writers = dict(enabled = write_bool("enabled"),
                   name = write_string("name"),
                   url = write_string("url"),
                   type = write_string("type"))


    def get_resources(self):
        res_url = url(self.catalog.service_url,
            ["workspaces", self.workspace.name, "coveragestores", self.name, "coverages.xml"])

        xml = self.catalog.get_xml(res_url)

        def cov_from_node(node):
            return coverage_from_index(self.catalog, self.workspace, self, node)

        return [cov_from_node(node) for node in xml.findall("coverage")]

class UnsavedCoverageStore(CoverageStore):
    save_method = "POST"

    def __init__(self, catalog, name, workspace):
        super(UnsavedCoverageStore, self).__init__(catalog, workspace, name)
        self.dirty.update(name=name, enabled = True, type="GeoTIFF",
                url = "file:data/")

    @property
    def href(self):
        return url(self.catalog.service_url,
            ["workspaces", self.workspace.name, "coveragestores"], dict(name=self.name))
