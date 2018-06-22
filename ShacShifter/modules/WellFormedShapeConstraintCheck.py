import logging
import rdflib
from rdflib.exceptions import UniquenessError
from .modules.WellFormedShape import WellFormedShape
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
class WellFormedShapeConstraintCheck:

    def __init__(self, graph):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        self.g = graph
        self.errors = list()

    def shaclListConstraint(self, listUri, datatype=None):
        """Checks for the Shacllist Constraints.

        args:    rdflib.term.URIRef or rdflib.term.BNode listUri
        returns: None
        """
        shaclList = list()
        uri = listUri
        lastListEntry = False

         while not lastListEntry:
            if not (type(uri) == rdflib.term.URIRef or type(uri) == rdflib.term.Bnode):
                self.errors.append('Wrong Type in shacllist:{}'.format(uri))
            if uri in shaclList:
                self.errors.append('Loop in the shacllist:{}'.format(uri))
            shaclList.append(uri)
            if not datatype is None:
                val = str(self.g.value(subject=uri, predicate=self.rdf.first))
                self.nodeKindConstraint(val, False, False, True)
                if val.datatype != datatype:
                    self.errors.append('Conflict found. Object has the wrong type:{}'.format(val))
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
                    self.errors.append('Conflict found. Object has the wrong type:{}'.format(object))
        else:
            correctType = False
            if isUri and type(object) is rdflib.term.URIRef:
                correctType = True
            if isBNode and type(object) is rdflib.term.BNode:
                correctType = True
            if isLiteral and type(object) is rdflib.term.literal:
                correctType = True
            if not correctType:
                self.errors.append('Conflict found. Object has the wrong type:{}'.format(object))

    def maxConstraint(self):
        """Checks for the max Constraints.

        args:    None
        returns: None
        """
        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.ignoredProperties, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.ignoredProperties))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.nodekind, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.nodekind))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.closed, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.closed))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.path, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.path))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.datatype, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.data))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minCount, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.minCount))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxCount, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.maxCount))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minExclusive, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.minExclusive))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minInclusive, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.minInclusive))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxExclusive, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.maxExclusive))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxInclusive, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.maxInclusive))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minLength, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.minLength))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxLength, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.maxLength))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.pattern, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.pattern))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.flags, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.flags))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.uniqueLang))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh['in'], any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh['in']))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.order, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.order))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.qualifiedValueShape))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapesDisjoint, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.qualifiedValueShapesDisjoint))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.qualifiedMinCount))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.qualifiedMaxCount))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.group, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.group))

    def checkConstraints(wellFormedShape):
        """Checks for the nodekind Constraints

        args:   WellFormedShape wellFormedShape
        returns: None
        """
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

        if wellFormedShape.isSet['datatype']:
            self.nodeKindConstraint(wellFormedShape.datatype, True, False, False)

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

        if wellFormedShape.isSet['uniqueLang']:
            self.nodeKindConstraint(wellFormedShape.uniqueLang, False, False, True)

        maxConstraint()



