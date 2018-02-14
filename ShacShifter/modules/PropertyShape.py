class PropertyShape:
    """The PropertyShape class."""

    def __init__(self):
        self.uri = ''
        self.path = ''
        self.classes = []
        self.dataType = ''
        self.minCount = ''
        self.maxCount = ''
        self.minExclusive = ''
        self.minInclusive = ''
        self.maxExclusive = ''
        self.MaxInclusive = ''
        self.minLength = ''
        self.maxLength = ''
        self.pattern = ''
        self.flags = ''
        self.languageIn = []
        self.uniqueLang = False
        self.equals = []
        self.disjoint = []
        self.lessThan = []
        self.lessThanOrEquals = []
        self.nodes = []
        self.qualifiedValueShape = ''
        self.qualifiedValueShapesDisjoint = False
        self.qualifiedMinCount = ''
        self.qualifiedMaxCount = ''
        self.hasValue = []
        self.shIn = []
        self.order = 0
        # self.sOr = []
        # self.sNot = []
        # self.sAnd = []
        # self.sXone = []
