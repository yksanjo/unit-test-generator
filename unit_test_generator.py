#!/usr/bin/env python3
"""
Unit Test Generator - Standalone tool for generating unit tests.

This tool focuses specifically on generating comprehensive unit tests
for Python functions and classes.
"""

import argparse
import ast
from pathlib import Path
from typing import Any, Dict, List
from analyzers.ast_analyzer import ASTAnalyzer
from analyzers.edge_detector import EdgeCaseDetector


class UnitTestGenerator:
    """Generates unit tests for Python functions and classes."""
    
    def __init__(self):
        self.ast_analyzer = ASTAnalyzer()
        self.edge_detector = EdgeCaseDetector()
        
    def generate(self, source_path: Path, output_path: Path) -> List[str]:
        """Generate unit tests from source code.
        
        Args:
            source_path: Path to source file or directory.
            output_path: Path to output directory for tests.
            
        Returns:
            List of generated test file paths.
        """
        # Parse source files
        if source_path.is_file():
            files = [source_path]
        else:
            files = list(source_path.rglob("*.py"))
        
        analysis = {
            "files": [],
            "functions": [],
            "classes": []
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                tree = ast.parse(source_code)
                functions = self.ast_analyzer.extract_functions(tree)
                classes = self.ast_analyzer.extract_classes(tree)
                
                analysis["files"].append(str(file_path))
                analysis["functions"].extend(functions)
                analysis["classes"].extend(classes)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        # Generate tests
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated = []
        
        # Generate function tests
        if analysis["functions"]:
            test_file = self._generate_function_tests(analysis["functions"], output_path)
            generated.append(test_file)
        
        # Generate class tests
        if analysis["classes"]:
            test_file = self._generate_class_tests(analysis["classes"], output_path)
            generated.append(test_file)
        
        return generated
    
    def _generate_function_tests(self, functions: List[Dict], output_path: Path) -> str:
        """Generate unit tests for functions."""
        test_file = output_path / "test_functions.py"
        
        lines = ['"""Unit tests for functions."""', '', 'import pytest', '']
        
        for func in functions:
            func_name = func.get('name', '')
            if func_name.startswith('_') and not func_name.startswith('__'):
                continue
                
            args = func.get('args', [])
            
            # Basic test
            lines.append(f'def test_{func_name}():')
            if args:
                arg_str = ', '.join(['1'] * len(args))
                lines.append(f'    result = {func_name}({arg_str})')
            else:
                lines.append(f'    result = {func_name}()')
            lines.append(f'    assert result is not None')
            lines.append('')
            
            # Edge case tests
            for arg in args:
                arg_name = arg.get('name', 'arg')
                lines.append(f'def test_{func_name}_{arg_name}_edge_cases():')
                lines.append(f'    # Test edge cases for {arg_name}')
                lines.append(f'    # Add your test cases here')
                lines.append('')
            
            # Error test
            lines.append(f'def test_{func_name}_error_handling():')
            lines.append(f'    with pytest.raises(Exception):')
            lines.append(f'        {func_name}(invalid_input)')
            lines.append('')
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(lines))
        
        return str(test_file)
    
    def _generate_class_tests(self, classes: List[Dict], output_path: Path) -> str:
        """Generate unit tests for classes."""
        test_file = output_path / "test_classes.py"
        
        lines = ['"""Unit tests for classes."""', '', 'import pytest', '']
        
        for cls in classes:
            class_name = cls.get('name', '')
            if class_name.startswith('_'):
                continue
            
            lines.append(f'class Test{class_name}:')
            lines.append('')
            
            # Init test
            lines.append('    def test_initialization(self):')
            lines.append(f'        instance = {class_name}()')
            lines.append('        assert instance is not None')
            lines.append('')
            
            # Method tests
            methods = cls.get('methods', [])
            for method in methods:
                method_name = method.get('name', '')
                if method_name.startswith('_'):
                    continue
                    
                lines.append(f'    def test_{method_name}(self):')
                lines.append(f'        instance = {class_name}()')
                lines.append(f'        result = instance.{method_name}()')
                lines.append(f'        assert result is not None')
                lines.append('')
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(lines))
        
        return str(test_file)


def main():
    parser = argparse.ArgumentParser(description="Unit Test Generator")
    parser.add_argument("--source", required=True, help="Source code path")
    parser.add_argument("--output", default="./tests", help="Output directory")
    
    args = parser.parse_args()
    
    generator = UnitTestGenerator()
    source = Path(args.source)
    output = Path(args.output)
    
    print(f"Generating unit tests from: {source}")
    print(f"Output directory: {output}")
    
    generated = generator.generate(source, output)
    
    print(f"\nGenerated {len(generated)} test files:")
    for f in generated:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
