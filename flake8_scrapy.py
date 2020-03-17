import ast

from finders.domains import (
    UnreachableDomainIssueFinder, UrlInAllowedDomainsIssueFinder,
)
from finders.oldstyle import OldSelectorIssueFinder, UrlJoinIssueFinder, BoolIssueFinder, IntIssueFinder, StringIssueFinder, ListIssueFinder, DictIssueFinder


__version__ = '0.0.1'


class ScrapyStyleIssueFinder(ast.NodeVisitor):

    def __init__(self, *args, **kwargs):
        super(ScrapyStyleIssueFinder, self).__init__(*args, **kwargs)
        self.issues = []
        self.finders = {
            'Assign': [
                UnreachableDomainIssueFinder(),
                UrlInAllowedDomainsIssueFinder(),
                OldSelectorIssueFinder(),
                BoolIssueFinder(),
                IntIssueFinder(),
                StringIssueFinder(),
                ListIssueFinder(),
                DictIssueFinder(),
            ],
            'Call': [
                UrlJoinIssueFinder(),
            ]
        }

    def find_issues_visitor(self, visitor, node):
        """Find issues for the provided visitor
        """
        for finder in self.finders[visitor]:
            issues = finder.find_issues(node)
            if issues:
                self.issues.extend(list(issues))
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.find_issues_visitor('Assign', node)

    def visit_Call(self, node):
        self.find_issues_visitor('Call', node)


class ScrapyStyleChecker(object):
    options = None
    name = 'flake8-scrapy'
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def run(self):
        finder = ScrapyStyleIssueFinder()
        finder.visit(self.tree)

        for line, col, msg in finder.issues:
            yield (line, col, msg, ScrapyStyleChecker)
