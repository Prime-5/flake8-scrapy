import ast
from finders import IssueFinder


class BoolIssueFinder(IssueFinder):

    msg_code = ' SET01'
    msg_info = 'Should be a boolean value'

    def find_issues(self, node):      
        if self.issue_applies(node):
            if not isinstance(node.value, ast.NameConstant):   
                print (node.lineno, node.col_offset, node.targets[0].id + self.message)
                    

    def issue_applies(self, node):
        items = ['ROBOTSTXT_OBEY', 'COOKIES_ENABLED', 'TELNETCONSOLE_ENABLED', 'AUTOTHROTTLE_ENABLED', 'AUTOTHROTTLE_DEBUG', 'HTTPCACHE_ENABLED']
        obj = node.targets[0].id
        for item in items:
            if(obj == item):
                return True



class IntIssueFinder(IssueFinder):

    msg_code = ' SET02'
    msg_info = 'Should be an integer'
        
    def find_issues(self, node):      
        if self.issue_applies(node):
            if not isinstance(node.value, ast.Num):   
                print (node.lineno, node.col_offset, node.targets[0].id + self.message)
                    

    def issue_applies(self, node):
        items = ['CONCURRENT_REQUESTS', 'DOWNLOAD_DELAY', 'CONCURRENT_REQUESTS_PER_DOMAIN', 'CONCURRENT_REQUESTS_PER_IP', 'AUTOTHROTTLE_START_DELAY', 'AUTOTHROTTLE_MAX_DELAY', 'AUTOTHROTTLE_TARGET_CONCURRENCY', 'HTTPCACHE_EXPIRATION_SECS']
        obj = node.targets[0].id
        for item in items:
            if(obj == item):
                return True            


class StringIssueFinder(IssueFinder):

    msg_code = ' SET03'
    msg_info = 'Should be a string'

    def find_issues(self, node):      
        if self.issue_applies(node):
            if not isinstance(node.value, ast.Str):   
                print (node.lineno, node.col_offset, node.targets[0].id + self.message)
                    

    def issue_applies(self, node):
        items = ['BOT_NAME', 'NEWSPIDER_MODULE', 'USER_AGENT', 'HTTPCACHE_DIR', 'HTTPCACHE_STORAGE']
        obj = node.targets[0].id
        for item in items:
            if(obj == item):
                return True


class ListIssueFinder(IssueFinder):

    msg_code = ' SET04'
    msg_info = 'Should be a list'

    def find_issues(self, node):      
        if self.issue_applies(node):
            if not isinstance(node.value, ast.List):   
                print (node.lineno, node.col_offset, node.targets[0].id + self.message)
                    

    def issue_applies(self, node):
        items = ['SPIDER_MODULES', 'HTTPCACHE_IGNORE_HTTP_CODES']
        obj = node.targets[0].id
        for item in items:
            if(obj == item):
                return True


class DictIssueFinder(IssueFinder):

    msg_code = ' SET05'
    msg_info = 'Should be a dictionary'

    def find_issues(self, node):      
        if self.issue_applies(node):
            if not isinstance(node.value, ast.Dict):   
                print (node.lineno, node.col_offset, node.targets[0].id + self.message)
                    

    def issue_applies(self, node):
        items = ['DEFAULT_REQUEST_HEADERS', 'SPIDER_MIDDLEWARES', 'DOWNLOADER_MIDDLEWARES', 'EXTENSIONS', 'ITEM_PIPELINES']
        obj = node.targets[0].id
        for item in items:
            if(obj == item):
                return True


class UrlJoinIssueFinder(IssueFinder):
    msg_code = 'SCP03'
    msg_info = 'urljoin(response.url, "/foo") can be replaced by response.urljoin("/foo")'

    def find_issues(self, node):
        if not self.issue_applies(node):
            return

        first_param = node.args[0]
        if not isinstance(first_param, ast.Attribute):
            return

        if first_param.value.id == 'response' and first_param.attr == 'url':
            # found it: first param to urljoin is response.url
            yield (node.lineno, node.col_offset, self.message)

    def issue_applies(self, node):
        return (
            isinstance(node.func, ast.Name) and
            node.func.id == 'urljoin' and
            node.args
        )


class OldSelectorIssueFinder(IssueFinder):
    msg_code = 'SCP04'
    msg_info = 'use response.selector or response.xpath or response.css instead'

    def is_response_dot_body_as_unicode(self, node):
        """ Returns True if node represents response.body_as_unicode()
        """
        return (
            isinstance(node, ast.Call) and
            isinstance(node.func, ast.Attribute) and
            node.func.value.id == 'response' and
            node.func.attr == 'body_as_unicode'
        )

    def is_response_dot_text_or_body(self, node):
        """ Return whether or not a node represents response.text or
            response.body
        """
        return (
            isinstance(node, ast.Attribute) and
            node.value.id == 'response' and
            node.attr in ('text', 'body')
        )

    def is_response(self, node):
        """ Check if node represents an object named as response
        """
        return (
            isinstance(node, ast.Name) and
            node.id == 'response'
        )

    def has_response_for_keyword_parameter(self, node):
        """ Check if response or response.text is passed as a keyword parameter
            as in: Selector(text=response.text) or Selector(response=response)
        """
        return (
            (
                node.arg == 'text' and
                self.is_response_dot_text_or_body(node.value) or
                self.is_response_dot_body_as_unicode(node.value)
            ) or (
                node.arg == 'response' and
                self.is_response(node.value)
            )
        )

    def issue_applies(self, node):
        return (
            isinstance(node.value, ast.Call) and
            isinstance(node.value.func, ast.Name) and
            node.value.func.id == 'Selector'
        )

    def find_issues(self, node):
        if not self.issue_applies(node):
            return

        # look for: Selector(response)
        if node.value.args:
            param = node.value.args[0]
            if self.is_response(param):
                return [(node.lineno, node.col_offset, self.message)]

        # look for: Selector(response=response) or Selector(text=response.text)
        for kw in node.value.keywords:
            if self.has_response_for_keyword_parameter(kw):
                return [(node.lineno, node.col_offset, self.message)]
