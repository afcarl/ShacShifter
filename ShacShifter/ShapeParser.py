#!/usr/bin/env python3

import logging
import rdflib
from rdflib.exceptions import UniquenessError
from .modules.WellFormedShape import WellFormedShape
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape


class ShapeParser:
    """A parser for SHACL Shapes."""

    logger = logging.getLogger('ShacShifter.ShapeParser')

    def __init__(self):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        self.g = rdflib.Graph()
        self.nodeShapes = {}
        self.propertyShapes = {}

    def parseShape(self, inputFilePath):
        """Parse a Shape given in a file.

        args: string inputFilePath
        returns: list of dictionaries for nodeShapes and propertyShapes
        """
        self.g.parse(inputFilePath, format='turtle')
        wellFormedShapeUris = self.getWellFormedShapeUris()

        for shapeUri in wellFormedShapeUris:
            wellFormedShape = self.parseWellFormedShape(shapeUri)
            self.wellFormedShapes[wellFormedShape.uri] = wellFormedShape

        return self.nodeShapes

    def getWellFormedShapeUris(self):
        """Get URIs of all Root Node shapes.

        returns: list of Node Shape URIs
        """
        wellFormedShapeUris = list()

        qres = self.g.query("""
            SELECT DISTINCT ?root
            WHERE {
                ?root ?s ?o .
                FILTER NOT EXISTS {?a ?b ?root .}
            }""")

        for row in qres:
            wellFormedShapeUris.append(row.root)

        return wellFormedShapeUris

    def getPropertyShapeCandidates(self):
        """Get all property shapes.

        The property shapes must not be nodeshape properties or used in sh:not, sh:and,
        sh:or or sh:xor

        returns: list of Property Shape URIs
        """
        propertyShapeUris = set()

        for stmt in self.g.subjects(self.sh.path, None):
            if (self.g.value(predicate=self.sh.property, object=stmt) is None and
                self.g.value(predicate=self.rdf.first, object=stmt) is None and
                self.g.value(predicate=self.sh['not'], object=stmt) is None):
                propertyShapeUris.add(stmt)

        return propertyShapeUris

    def parseWellFormedShape(self, shapeUri):
        """Parse a WellFormedShape given by its URI.

        args:    string shapeUri
        returns: object WellFormedShape/NodeShape/PropertyShape
        """
        wellFormedShape = WellFormedShape()
        # if empty "URI's" are bad change it later on to add Blanknodes too
        if shapeUri != rdflib.term.BNode(shapeUri):
            wellFormedShape.isSet['uri'] = True
            wellFormedShape.uri = str(shapeUri)

        for stmt in self.g.objects(shapeUri, self.sh.targetClass):
            wellFormedShape.isSet['targetClass'] = True
            wellFormedShape.targetClass.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetNode):
            wellFormedShape.isSet['targetNode'] = True
            wellFormedShape.targetNode.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetObjectsOf):
            wellFormedShape.isSet['targetObjectsOf'] = True
            wellFormedShape.targetObjectsOf.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetSubjectsOf):
            wellFormedShape.isSet['targetSubjectsOf'] = True
            wellFormedShape.targetSubjectsOf.append(str(stmt))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.ignoredProperties, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.ignoredProperties)
            )
        if val is not None:
            self.shaclListConstraint(val)
            wellFormedShape.isSet['ignoredProperties'] = True
            properties = val
            lastListEntry = False

            while not lastListEntry:
                wellFormedShape.ignoredProperties.append(
                    str(self.g.value(subject=properties, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if self.g.value(subject=properties, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                properties = self.g.value(subject=properties, predicate=self.rdf.rest)

        for stmt in self.g.objects(shapeUri, self.sh.message):
            wellFormedShape.isSet['message'] = True
            if (stmt.language is None):
                if(str(stmt.datatype) != 'http://www.w3.org/2001/XMLSchema#string')
                    wellFormedShape.message['default'] = str(stmt)
                else:
                    raise Exception(
                        'Conflict found. Literal has neither xsd:string nor language tag:{}'
                        .format(self.sh.stmt)
                    )
            else:
                wellFormedShape.message[stmt.language] = str(stmt)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.nodeKind, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.nodeKind)
            )
        if val is not None:
            wellFormedShape.isSet['nodeKind'] = True
            wellFormedShape.nodeKind = str(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.closed, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.closed))
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#boolean':
                raise Exception('Conflict found. Boolean has the wrong type {}'.format(self.sh.closed))
            wellFormedShape.isSet['closed'] = True
            if (str(val).lower() == "true"):
                wellFormedShape.closed = True

        for stmt in self.g.objects(shapeUri, self.sh.property):
            wellFormedShape.isSet['property'] = True
            propertyShape = self.parseWellFormedShape(stmt)
            self.propertyShapes[stmt] = propertyShape
            wellFormedShape.properties.append(propertyShape)

        try:
            pathStart = self.g.value(subject=shapeUri, predicate=self.sh.path, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.path))
        if pathStart is not None:
            self.shaclListConstraint(pathStart)
            wellFormedShape.path = self.getPropertyPath(pathStart)

        for stmt in self.g.objects(shapeUri, self.sh['class']):
            wellFormedShape.isSet['classes'] = True
            wellFormedShape.classes.append(str(stmt))

        val = self.g.value(subject=shapeUri, predicate=self.sh['name'])
        if val is not None:
            wellFormedShape.isSet['name'] = True
            wellFormedShape.name = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh['description'])
        if val is not None:
            wellFormedShape.isSet['description'] = True
            wellFormedShape.description = str(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.datatype, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.datatype))
        if val is not None:
            wellFormedShape.isSet['dataType'] = True
            wellFormedShape.dataType = str(val)

        try:
            minCount = self.g.value(subject=shapeUri, predicate=self.sh.minCount, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.minCount))
        if minCount is not None:
            if str(minCount.datatype) != 'http://www.w3.org/2001/XMLSchema#integer':
                raise Exception('Conflict found. Number has the wrong type {}'.format(self.sh.minCount))
            wellFormedShape.isSet['minCount'] = True
            wellFormedShape.minCount = int(minCount)

        try:
            maxCount = self.g.value(subject=shapeUri, predicate=self.sh.maxCount, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.maxCount))
        if maxCount is not None:
            if str(maxCount.datatype) != 'http://www.w3.org/2001/XMLSchema#integer':
                raise Exception('Conflict found. Number has the wrong type {}'.format(self.sh.maxCount))
            wellFormedShape.isSet['maxCount'] = True
            wellFormedShape.maxCount = int(maxCount)
            if (wellFormedShape.isSet['minCount'] and
                    wellFormedShape.minCount > wellFormedShape.maxCount):
                raise Exception(
                    'Conflict found. sh:maxCount {} must be greater or eqal sh:minCount {}'
                    .format(wellFormedShape.maxCount, wellFormedShape.minCount))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minExclusive, any=False)
                    except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.minExclusive)
            )
        if val is not None:
            wellFormedShape.isSet['minExclusive'] = True
            wellFormedShape.minExclusive = int(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minInclusive, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.minInxclusive)
            )
        if val is not None:
            wellFormedShape.isSet['minInclusive'] = True
            wellFormedShape.minInclusive = int(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxExclusive, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.maxExclusive)
            )
        if val is not None:
            wellFormedShape.isSet['maxExclusive'] = True
            wellFormedShape.maxExclusive = int(val)
            if (wellFormedShape.isSet['minExclusive'] and
                    wellFormedShape.minExclusive > wellFormedShape.maxExclusive):
                raise Exception(
                    'Conflict found. sh:maxExclusive {} must be greater or eqal sh:minExclusive {}'
                    .format(wellFormedShape.maxExclusive, wellFormedShape.minExclusive))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxInclusive, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.maxInclusive)
            )
        if val is not None:
            wellFormedShape.isSet['maxInclusive'] = True
            wellFormedShape.maxInclusive = int(val)
            if (wellFormedShape.isSet['minInclusive'] and
                    wellFormedShape.minInclusive > wellFormedShape.maxInclusive):
                raise Exception(
                    'Conflict found. sh:maxInclusive {} must be greater or eqal sh:minInclusive {}'
                    .format(wellFormedShape.maxInclusive, wellFormedShape.minInclusive))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minLength, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.minLength))
        if val is not None:
            if str(val.datatype) != 'http://www.w3.org/2001/XMLSchema#integer':
                raise Exception('Conflict found. Number has the wrong type {}'.format(self.sh.minLength))
            wellFormedShape.isSet['minLength'] = True
            wellFormedShape.minLength = int(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxLength, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.maxLength))
        if val is not None:
            if str(val.datatype) != 'http://www.w3.org/2001/XMLSchema#integer':
                raise Exception('Conflict found. Number has the wrong type {}'.format(self.sh.maxLength))
            wellFormedShape.isSet['maxLength'] = True
            wellFormedShape.maxLength = int(val)
            if (wellFormedShape.isSet['minLength'] and
                    wellFormedShape.minLength > wellFormedShape.maxLength):
                raise Exception(
                    'Conflict found. sh:maxLength {} must be greater or eqal sh:minLength {}'
                    .format(wellFormedShape.maxLength, wellFormedShape.minLength))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.pattern, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.pattern))
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#string':
                raise Exception('Conflict found. String has the wrong type {}'.format(self.sh.pattern))
            wellFormedShape.isSet['pattern'] = True
            wellFormedShape.pattern = str(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.flags, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.flags))
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#string':
                raise Exception('Conflict found. String has the wrong type {}'.format(self.sh.flags))
            wellFormedShape.isSet['flags'] = True
            wellFormedShape.flags = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.languageIn)
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#string':
                raise Exception('Conflict found. String has the wrong type {}'.format(self.sh.languageIn))
            self.shaclListConstraint(val)
            wellFormedShape.isSet['languageIn'] = True
            languages = val
            lastListEntry = False

            while not lastListEntry:
                wellFormedShape.languageIn.append(
                    str(self.g.value(subject=languages, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if self.g.value(subject=languages, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                languages = self.g.value(subject=languages, predicate=self.rdf.rest)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.uniqueLang)
            )
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#boolean':
                raise Exception('Conflict found. String has the wrong type {}'.format(self.sh.uniqueLang))
            wellFormedShape.isSet['uniqueLang'] = True
            if (str(val).lower() == "true"):
                wellFormedShape.uniqueLang = True

        for stmt in self.g.objects(shapeUri, self.sh.equals):
            wellFormedShape.isSet['equals'] = True
            wellFormedShape.equals.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.disjoint):
            wellFormedShape.isSet['disjoint'] = True
            wellFormedShape.disjoint.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.lessThan):
            wellFormedShape.isSet['lessThan'] = True
            wellFormedShape.lessThan.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.lessThanOrEquals):
            wellFormedShape.isSet['lessThanOrEquals'] = True
            wellFormedShape.lessThanOrEquals.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.node):
            wellFormedShape.isSet['node'] = True
            wellFormedShape.nodes.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.hasValue):
            wellFormedShape.isSet['hasValue'] = True
            wellFormedShape.hasValue.append(stmt)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh['in'], any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh['in']))
        if val is not None:
            self.shaclListConstraint(val)
            wellFormedShape.isSet['shIn'] = True
            lastListEntry = False

            while True:
                first_value = self.g.value(subject=val, predicate=self.rdf.first, any=False)
                rest_value = self.g.value(subject=val, predicate=self.rdf.rest, any=False)
                wellFormedShape.shIn.append(first_value)
                # check if this was the last entry in the list
                if rest_value == self.rdf.nil:
                    break
                val = rest_value

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.order, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.order))
        if val is not None:
            wellFormedShape.isSet['order'] = True
            wellFormedShape.order = int(val)
        
        #QVS can have multiple Instances per Path, but every ProperyShape can only have 1
        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.qualifiedValueShape)
            )
        if val is not None:
            wellFormedShape.isSet['qualifiedValueShape'] = True
            wellFormedShape.qualifiedValueShape = self.parseWellFormedShape(val)

        try:
            val = self.g.value(
                subject=shapeUri, predicate=self.sh.qualifiedValueShapesDisjoint, any=False
            )
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'
                .format(self.sh.qualifiedValueShapesDisjoint)
            )
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#boolean':
                raise Exception('Conflict found. String has the wrong type {}'.format(self.sh.qualifiedValueShapesDisjoint))
            wellFormedShape.isSet['qualifiedValueShapesDisjoint'] = True
            if (str(val).lower() == "true"):
                wellFormedShape.qualifiedValueShapesDisjoint = True
                # TODO check Sibling Shapes

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.qualifiedMinCount)
            )
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#integer':
                raise Exception('Conflict found. Integer has the wrong type {}'.format(self.sh.qualifiedMinCount))
            wellFormedShape.isSet['qualifiedMinCount'] = True
            wellFormedShape.qualifiedMinCount = int(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount, any=False)
        except UniquenessError:
            raise Exception(
                'Conflict found. More than one value for {}'.format(self.sh.qualifiedMaxCount)
            )
        if val is not None:
            if str(val.datatype) != 'ttp://www.w3.org/2001/XMLSchema#integer':
                raise Exception('Conflict found. Integer has the wrong type {}'.format(self.sh.qualifiedMaxCount))
            if (wellFormedShape.isSet['qualifiedMinCount'] and
                    wellFormedShape.qualifiedMinCount > int(val)):
                raise Exception('sh:qualifiedMinCount greater than sh:qualifiedMaxCount.')
            wellFormedShape.isSet['qualifiedMaxCount'] = True
            wellFormedShape.qualifiedMaxCount = int(val)

        for stmt in self.g.objects(shapeUri, self.sh.message):
            wellFormedShape.isSet['message'] = True
            if (stmt.language is None):
                wellFormedShape.message['default'] = str(stmt)
            else:
                wellFormedShape.message[stmt.language] = str(stmt)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.group, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.group))
        if val is not None:
            wellFormedShape.isSet['group'] = True
            wellFormedShape.group = self.parseWellFormedShape(val)

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.order, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.order))
        if val is not None:
            wellFormedShape.isSet['order'] = True
            wellFormedShape.group = int(val)

        self.checkConstraints(wellFormedShape)

        try:
            propertyShape = PropertyShape()
            propertyShape.fill(wellFormedShape)
            shape = propertyShape
        except TypeError:
            try:
                nodeShape = NodeShape()
                nodeShape.fill(wellFormedShape)
                shape = nodeShape
            except TypeError:
                shape = wellFormedShape

        return shape

    def getPropertyPath(self, pathUri):
        # not enforcing blank nodes here, but stripping the link nodes from the data structure
        newPathUri = self.g.value(subject=pathUri, predicate=self.rdf.first)
        if newPathUri is not None:
            rdfList = []
            rdfList.append(self.getPropertyPath(newPathUri))

            if not (self.g.value(subject=pathUri, predicate=self.rdf.rest) == self.rdf.nil):
                newPathUri = self.g.value(subject=pathUri, predicate=self.rdf.rest)
                rest = self.getPropertyPath(newPathUri)
                if (isinstance(rest, list)):
                    rdfList += rest
                else:
                    rdfList.append(rest)

            return rdfList

        altPath = self.g.value(subject=pathUri, predicate=self.sh.alternativePath)
        if altPath is not None:
            # newPathUri = altPath
            rdfDict = {self.sh.alternativePath: self.getPropertyPath(altPath)}
            return rdfDict

        invPath = self.g.value(subject=pathUri, predicate=self.sh.inversePath)
        if invPath is not None:
            rdfDict = {self.sh.inversePath: self.getPropertyPath(invPath)}
            return rdfDict

        zeroOrMorePath = self.g.value(subject=pathUri, predicate=self.sh.zeroOrMorePath)
        if zeroOrMorePath is not None:
            rdfDict = {self.sh.zeroOrMorePath: self.getPropertyPath(zeroOrMorePath)}
            return rdfDict

        oneOrMorePath = self.g.value(subject=pathUri, predicate=self.sh.oneOrMorePath)
        if oneOrMorePath is not None:
            rdfDict = {self.sh.oneOrMorePath: self.getPropertyPath(oneOrMorePath)}
            return rdfDict

        zeroOrOnePath = self.g.value(subject=pathUri, predicate=self.sh.zeroOrOnePath)
        if zeroOrOnePath is not None:
            rdfDict = {self.sh.zeroOrOnePath: self.getPropertyPath(zeroOrOnePath)}
            return rdfDict

        # last Object in this Pathpart, check if its an Uri and return it
        if isinstance(pathUri, rdflib.term.URIRef):
            return str(pathUri)
        else:
            raise Exception('Object of sh:path is no URI')

    def shaclListConstraint(self, listUri):
        """Checks for the Shacllist Constraints.

        args:    rdflib.term.URIRef or rdflib.term.BNode listUri
        returns: None
        """
        shaclList = list()
        uri = listUri
        lastListEntry = False

         while not lastListEntry:
            if not (type(uri) == rdflib.term.URIRef or type(uri) == rdflib.term.Bnode):
                raise Exception('Wrong Type in shacllist')
            if uri in shaclList:
                raise Exception('Loop in the shacllist')
            shaclList.append(
                str(self.g.value(subject=uri, predicate=self.rdf.first))
            )
            # check if this was the last entry in the list
            if self.g.value(subject=uri, predicate=self.rdf.rest) == self.rdf.nil:
                lastListEntry = True
            properties = self.g.value(subject=uri, predicate=self.rdf.rest)

    def nodeKindConstraint(self, object, isUri, isBNode, isLiteral):
        """Checks for the nodekind Constraints.

        args:    list or rdflib.term.URIRef or rdflib.term.BNode or rdflib.term.literal object
                 boolean isUri
                 boolean isBNode
                 boolean isLiteral
        returns: None
        """
        if type(object) is list:
            for obj in object:
                correctType = False
                if isUri and type(object) is rdflib.term.URIRef:
                    correctType = True
                if isBNode and type(object) is rdflib.term.BNode:
                    correctType = True
                if isLiteral and type(object) is rdflib.term.literal:
                    correctType = True
                if not correctType:
                    raise Exception('Conflict found. Object has the wrong type:{}'.format(object))
        else:
            correctType = False
            if isUri and type(object) is rdflib.term.URIRef:
                correctType = True
            if isBNode and type(object) is rdflib.term.BNode:
                correctType = True
            if isLiteral and type(object) is rdflib.term.literal:
                correctType = True
            if not correctType:
                raise Exception('Conflict found. Object has the wrong type:{}'.format(object))
    def checkConstraints(wellFormedShape):
        # TODO add full constraint check (e.g. sh:A and sh:B can't be in the
        # same Shape or sh:C can only be in Propertyshapes)
        # sh:entailment is ignored (should we add it?)
        # shape constraint is tested through the whole process?
        # multiple parameters and generally all "only one instance" checks are in in the parse function
        # path constraints are kinda loosened (allow uris) and checked in the actual parse i guess?
        # how to check pattern regex being sparql valid?
        # node kind constraints:
        if wellFormedShape.isSet['targetNode']:
            self.nodeKindConstraint(wellFormedShape.targetNode, True, False, True)

        if wellFormedShape.isSet['targetClass']:
            self.nodeKindConstraint(wellFormedShape.targetClass, True, False, False)

        if wellFormedShape.isSet['targetSubjectsOf']:
            self.nodeKindConstraint(wellFormedShape.targetSubjectsOf, True, False, False)

        if wellFormedShape.isSet['targetObjectsOf']:
            self.nodeKindConstraint(wellFormedShape.targetObjectsOf, True, False, False)

        if wellFormedShape.isSet['classes']:
            self.nodeKindConstraint(wellFormedShape.classes, True, False, False)

        if wellFormedShape.isSet['dataType']:
            self.nodeKindConstraint(wellFormedShape.dataType, True, False, False)

        if wellFormedShape.isSet['minCount']:
            self.nodeKindConstraint(wellFormedShape.minCount, False, False, True)

        if wellFormedShape.isSet['maxCount']:
            self.nodeKindConstraint(wellFormedShape.maxCount, False, False, True)

        if wellFormedShape.isSet['minExclusive']:
            self.nodeKindConstraint(wellFormedShape.minExclusive, False, False, True)

        if wellFormedShape.isSet['minInclusive']:
            self.nodeKindConstraint(wellFormedShape.minInclusive, False, False, True)

        if wellFormedShape.isSet['maxExclusive']:
            self.nodeKindConstraint(wellFormedShape.maxExclusive, False, False, True)

        if wellFormedShape.isSet['maxInclusive']:
            self.nodeKindConstraint(wellFormedShape.maxInclusive, False, False, True)

        if wellFormedShape.isSet['equals']:
            self.nodeKindConstraint(wellFormedShape.equals, True, False, False)

        if wellFormedShape.isSet['disjoint']:
            self.nodeKindConstraint(wellFormedShape.disjoint, True, False, False)

        if wellFormedShape.isSet['lessThan']:
            self.nodeKindConstraint(wellFormedShape.lessThan, True, False, False)

        if wellFormedShape.isSet['lessThanOrEquals']:
            self.nodeKindConstraint(wellFormedShape.lessThanOrEquals, True, False, False)

        if wellFormedShape.isSet['ignoredProperties']:
            self.nodeKindConstraint(wellFormedShape.ignoredProperties, True, False, False)

        if wellFormedShape.isSet['flags']:
            self.nodeKindConstraint(wellFormedShape.flags, False, False, True)

        if wellFormedShape.isSet['pattern']:
            self.nodeKindConstraint(wellFormedShape.pattern, False, False, True)

        if wellFormedShape.isSet['languageIn']:
            self.nodeKindConstraint(wellFormedShape.languageIn, False, False, True)

        if wellFormedShape.isSet['uniqueLang']:
            self.nodeKindConstraint(wellFormedShape.uniqueLang, False, False, True)

        if wellFormedShape.isSet['qualifiedValueShapesDisjoint']:
            self.nodeKindConstraint(
                wellFormedShape.qualifiedValueShapesDisjoint, False, False, True
            )

        if wellFormedShape.isSet['qualifiedMinCount']:
            self.nodeKindConstraint(wellFormedShape.qualifiedMinCount, False, False, True)

        if wellFormedShape.isSet['qualifiedMaxCount']:
            self.nodeKindConstraint(wellFormedShape.qualifiedMaxCount, False, False, True)

        if wellFormedShape.isSet['closed']:
            self.nodeKindConstraint(wellFormedShape.closed, False, False, True)
