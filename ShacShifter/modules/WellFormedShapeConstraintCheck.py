import logging
import rdflib
from rdflib.exceptions import UniquenessError
from .modules.WellFormedShape import WellFormedShape
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .modules.Exceptions import 
class WellFormedShapeConstraintCheck:

    def __init__(self, graph, shapeUri):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        self.xsd = rdflib.NameSpace('http://www.w3.org/2001/XMLSchema#')
        self.g = graph
        self.shapeUri = shapeUri
        self.errors = list()
        self.checkConstraints()

    def shaclListConstraint(self, listUri, nodeKind=None, datatype=None):
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
            if not nodeKind is None:
                val = str(self.g.value(subject=uri, predicate=self.rdf.first))
                self.nodeKindConstraint(val, nodeKind[0], nodeKind[1], nodeKind[2])
            if not datatype is None:
                val = str(self.g.value(subject=uri, predicate=self.rdf.first))
                self.datatypeConstraint(val, datatype)
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
        correctType = False
        if isUri and type(object) is rdflib.term.URIRef:
            correctType = True
        if isBNode and type(object) is rdflib.term.BNode:
            correctType = True
        if isLiteral and type(object) is rdflib.term.literal:
            correctType = True
        if not correctType:
            self.errors.append(NodeKindConstraintError('Conflict found. Object has the wrong type:{}'.format(object)))

    def datatypeConstraint(self, object, datatype):

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

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.languageIn, any=False)
        except UniquenessError:
            self.errors.append('Conflict found for {}'.format(self.sh.languageIn))

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
        # list constraints

        val = self.g.value(subject=shapeUri, predicate=self.sh.languageIn)
        if val is not None:
            self.shaclListConstraint(val, None, self.xsd.string)

        val = self.g.value(subject=shapeUri, predicate=self.sh.ignoredProperties)
        if val is not None:
            self.shaclListConstraint(val, [True, False, False], None)

        val = self.g.value(subject=shapeUri, predicate=self.sh['in'])
        if val is not None:
            self.shaclListConstraint(val, None, None)

        # node kind constraints with multiple values:
        for stmt in self.g.objects(shapeUri, self.sh.targetNode)
            self.nodeKindConstraint(stmt, True, False, True)

        for stmt in self.g.objects(shapeUri, self.sh.targetClass)
            self.nodeKindConstraint(stmt, True, False, False)

        for stmt in self.g.objects(shapeUri, self.sh.targetSubjectsOf)
            self.nodeKindConstraint(stmt, True, False, False)

        for stmt in self.g.objects(shapeUri, self.sh.targetObjectsOf)
            self.nodeKindConstraint(stmt, True, False, False)

        for stmt in self.g.objects(shapeUri, self.sh.classes)
            self.nodeKindConstraint(stmt, True, False, False)

        for stmt in self.g.objects(shapeUri, self.sh.equals)
            self.nodeKindConstraint(stmt, True, False, False)

        for stmt in self.g.objects(shapeUri, self.sh.disjoint)
            self.nodeKindConstraint(stmt, True, False, False)

        for stmt in self.g.objects(shapeUri, self.sh.lessThan)
            self.nodeKindConstraint(stmt, True, False, False)

        for stmt in self.g.objects(shapeUri, self.sh.lessThanOrEquals)
            self.nodeKindConstraint(stmt, True, False, False)

        # node kind constraints with single values
        val = self.g.value(subject=shapeUri, predicate=self.sh.datatype)
        if val is not None:
            self.nodeKindConstraint(val, True, False, False)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minCount)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxCount)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minExclusive)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minInclusive)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxExclusive)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxInclusive)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.flags)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.pattern)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapesDisjoint)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        val = self.g.value(subject=shapeUri, predicate=self.sh.closed)
        if val is not None:
            self.nodeKindConstraint(val, False, False, True)

        maxConstraint()

        # datatype constraints (message, rest)

