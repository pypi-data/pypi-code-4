''' Discovery document generation.


{
  "kind": "discovery#directoryList",
  "discoveryVersion": "v1",
  "items": [
    {
      "kind": "discovery#directoryItem",
      "id": string,
      "name": string,
      "version": string,
      "title": string,
      "description": string,
      "discoveryRestUrl": string,
      "discoveryLink": string,
      "icons": {
        "x16": string,
        "x32": string
      },
      "documentationLink": string,
      "labels": [
        string
      ],
      "preferred": boolean
    }
  ]
}




'''


class DirectoryListGenerator(object):
    def __init__(self, apis):
        pass


class RestDescriptionGenerator(object):
    def __init__(self, services):
        # merge the various services into one namespspace
        pass
    
    def to_json(self):
        pass
    

class RestMethod(object):
    pass

class RestParameter(object):
    id = None
    type = None
    _ref = None
    description = None
    default = None
    required = None
    format = None
    pattern = None
    minimum = None
    maximum = None
    enum = None
    enum_descriptions = None
    repeated = False
    location = None
    properties = None
    additional_properties = None
    items = None
    annotations = None
    
class RestDescription(object):
    discovery_version = 'v1'
    id = None
    name = None
    version = None
    title = None
    description = None
    protocol = 'rest'
    root_url = None
    service_path = None
    parameters = None
    schemas = None
    methods = None
    
    

'''    
{
  "kind": "discovery#restDescription",
  "discoveryVersion": "v1",
  "id": string,
  "name": string,
  "version": string,
  "revision": string,
  "title": string,
  "description": string,
  "icons": {
    "x16": string,
    "x32": string
  },
  "documentationLink": string,
  "labels": [
    string
  ],
  "protocol": "rest",
  "baseUrl": string,
  "basePath": string,
  "rootUrl": string,
  "servicePath": string,
  "batchPath": "batch",
  "parameters": {
    (key): {
      "id": string,
      "type": string,
      "$ref": string,
      "description": string,
      "default": string,
      "required": boolean,
      "format": string,
      "pattern": string,
      "minimum": string,
      "maximum": string,
      "enum": [
        string
      ],
      "enumDescriptions": [
        string
      ],
      "repeated": boolean,
      "location": string,
      "properties": {
        (key): (JsonSchema)
      },
      "additionalProperties": (JsonSchema),
      "items": (JsonSchema),
      "annotations": {
        "required": [
          string
        ]
      }
    }
  },
  "auth": {
    "oauth2": {
      "scopes": {
        (key): {
          "description": string
        }
      }
    }
  },
  "features": [
    string
  ],
  "schemas": {
    (key): {
      "id": string,
      "type": string,
      "$ref": string,
      "description": string,
      "default": string,
      "required": boolean,
      "format": string,
      "pattern": string,
      "minimum": string,
      "maximum": string,
      "enum": [
        string
      ],
      "enumDescriptions": [
        string
      ],
      "repeated": boolean,
      "location": string,
      "properties": {
        (key): (JsonSchema)
      },
      "additionalProperties": (JsonSchema),
      "items": (JsonSchema),
      "annotations": {
        "required": [
          string
        ]
      }
    }
  },
  "methods": {
    (key): {
      "id": string,
      "path": string,
      "httpMethod": string,
      "description": string,
      "parameters": {
        (key): {
          "id": string,
          "type": string,
          "$ref": string,
          "description": string,
          "default": string,
          "required": boolean,
          "format": string,
          "pattern": string,
          "minimum": string,
          "maximum": string,
          "enum": [
            string
          ],
          "enumDescriptions": [
            string
          ],
          "repeated": boolean,
          "location": string,
          "properties": {
            (key): (JsonSchema)
          },
          "additionalProperties": (JsonSchema),
          "items": (JsonSchema),
          "annotations": {
            "required": [
              string
            ]
          }
        }
      },
      "parameterOrder": [
        string
      ],
      "request": {
        "$ref": string
      },
      "response": {
        "$ref": string
      },
      "scopes": [
        (value)
      ],
      "supportsMediaDownload": boolean,
      "supportsMediaUpload": boolean,
      "mediaUpload": {
        "accept": [
          string
        ],
        "maxSize": string,
        "protocols": {
          "simple": {
            "multipart": true,
            "path": string
          },
          "resumable": {
            "multipart": true,
            "path": string
          }
        }
      },
      "supportsSubscription": boolean
    }
  },
  "resources": {
    (key): {
      "methods": {
        (key): {
          "id": string,
          "path": string,
          "httpMethod": string,
          "description": string,
          "parameters": {
            (key): {
              "id": string,
              "type": string,
              "$ref": string,
              "description": string,
              "default": string,
              "required": boolean,
              "format": string,
              "pattern": string,
              "minimum": string,
              "maximum": string,
              "enum": [
                string
              ],
              "enumDescriptions": [
                string
              ],
              "repeated": boolean,
              "location": string,
              "properties": {
                (key): (JsonSchema)
              },
              "additionalProperties": (JsonSchema),
              "items": (JsonSchema),
              "annotations": {
                "required": [
                  string
                ]
              }
            }
          },
          "parameterOrder": [
            string
          ],
          "request": {
            "$ref": string
          },
          "response": {
            "$ref": string
          },
          "scopes": [
            (value)
          ],
          "supportsMediaDownload": boolean,
          "supportsMediaUpload": boolean,
          "mediaUpload": {
            "accept": [
              string
            ],
            "maxSize": string,
            "protocols": {
              "simple": {
                "multipart": true,
                "path": string
              },
              "resumable": {
                "multipart": true,
                "path": string
              }
            }
          },
          "supportsSubscription": boolean
        }
      },
      "resources": {
        (key): (RestResource)
      }
    }
  }
}'''