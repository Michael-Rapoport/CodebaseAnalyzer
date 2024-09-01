import re

class DependencyAnalyzer:
    def analyze_dependencies(self, code):
        dependencies = []
        import_pattern = re.compile(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', re.MULTILINE)
        
        for match in import_pattern.finditer(code):
            if match.group(1):  # from ... import ...
                dependencies.append(match.group(1))
            else:  # import ...
                dependencies.extend(name.strip() for name in match.group(2).split(','))
        
        return list(set(dependencies))  # Remove duplicates