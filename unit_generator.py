"""Unit Test Generator - Generates unit tests for functions and classes."""

import ast
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class UnitTestGenerator:
    """Generates unit tests for Python functions and classes."""
    
    def __init__(self):
        self.test_count = 0
        
    def generate(self, analysis: Dict[str, Any], output_path: Path) -> List[str]:
        """Generate unit tests based on analysis results.
        
        Args:
            analysis: Analysis results containing functions and classes.
            output_path: Path to output directory for test files.
            
        Returns:
            List of generated test file paths.
        """
        generated_files = []
        
        functions = analysis.get('functions', [])
        classes = analysis.get('classes', [])
        
        # Generate tests for functions
        if functions:
            test_file = self._generate_function_tests(functions, output_path)
            if test_file:
                generated_files.append(test_file)
        
        # Generate tests for classes
        if classes:
            test_file = self._generate_class_tests(classes, output_path)
            if test_file:
                generated_files.append(test_file)
        
        return generated_files
    
    def _generate_function_tests(self, functions: List[Dict], output_path: Path) -> str:
        """Generate unit tests for functions.
        
        Args:
            functions: List of function information.
            output_path: Path to output directory.
            
        Returns:
            Path to generated test file.
        """
        test_file = output_path / "test_functions.py"
        
        test_content = []
        test_content.append('"""Unit tests for functions."""')
        test_content.append('')
        test_content.append('import pytest')
        test_content.append('from unittest.mock import Mock, patch')
        test_content.append('')
        test_content.append('')
        
        for func in functions:
            test_content.extend(self._generate_function_test_cases(func))
            test_content.append('')
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write('\n'.join(test_content))
        
        return str(test_file)
    
    def _generate_function_test_cases(self, func: Dict) -> List[str]:
        """Generate test cases for a single function.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of test case code lines.
        """
        func_name = func.get('name', 'unknown')
        args = func.get('args', [])
        
        test_cases = []
        
        # Skip private functions
        if func_name.startswith('_') and not func_name.startswith('__'):
            return test_cases
        
        # Class for the function
        test_cases.append(f'def test_{func_name}_basic():')
        
        # Generate test code based on function signature
        if args:
            # Create test inputs based on argument types
            test_inputs = []
            for arg in args:
                arg_type = arg.get('annotation', '')
                test_input = self._get_test_value_for_type(arg_type)
                test_inputs.append(test_input)
            
            # Generate the function call
            call_args = ', '.join(test_inputs)
            test_cases.append(f'    # Test {func_name} with basic inputs')
            test_cases.append(f'    result = {func_name}({call_args})')
            test_cases.append(f'    assert result is not None  # Add your assertion')
        else:
            test_cases.append(f'    # Test {func_name} with no arguments')
            test_cases.append(f'    result = {func_name}()')
            test_cases.append(f'    assert result is not None  # Add your assertion')
        
        test_cases.append('')
        
        # Edge case tests
        test_cases.extend(self._generate_edge_case_tests(func))
        
        # Error handling tests
        test_cases.extend(self._generate_error_tests(func))
        
        return test_cases
    
    def _generate_edge_case_tests(self, func: Dict) -> List[str]:
        """Generate edge case tests for a function.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of test case code lines.
        """
        func_name = func.get('name', 'unknown')
        args = func.get('args', [])
        
        test_cases = []
        
        # Generate edge case tests for each argument
        for i, arg in enumerate(args):
            arg_type = arg.get('annotation', '')
            arg_name = arg.get('name', f'arg{i}')
            
            # Test with None
            test_cases.append(f'def test_{func_name}_{arg_name}_none():')
            test_cases.append(f'    # Test with None value')
            
            test_inputs = []
            for j, a in enumerate(args):
                if j == i:
                    test_inputs.append('None')
                else:
                    test_input = self._get_test_value_for_type(a.get('annotation', ''))
                    test_inputs.append(test_input)
            
            call_args = ', '.join(test_inputs)
            test_cases.append(f'    # result = {func_name}({call_args})')
            test_cases.append(f'    # Add your assertion or expect error')
            test_cases.append('')
            
            # Test with empty values for collections
            if arg_type in ['list', 'List', 'str', 'str', 'dict', 'Dict', 'set', 'Set']:
                test_cases.append(f'def test_{func_name}_{arg_name}_empty():')
                test_cases.append(f'    # Test with empty {arg_type}')
                
                test_inputs = []
                for j, a in enumerate(args):
                    if j == i:
                        if arg_type in ['list', 'List']:
                            test_inputs.append('[]')
                        elif arg_type in ['str', 'str']:
                            test_inputs.append('""')
                        elif arg_type in ['dict', 'Dict']:
                            test_inputs.append('{}')
                        elif arg_type in ['set', 'Set']:
                            test_inputs.append('set()')
                        else:
                            test_inputs.append(self._get_test_value_for_type(a.get('annotation', '')))
                    else:
                        test_input = self._get_test_value_for_type(a.get('annotation', ''))
                        test_inputs.append(test_input)
                
                call_args = ', '.join(test_inputs)
                test_cases.append(f'    # result = {func_name}({call_args})')
                test_cases.append(f'    # Add your assertion')
                test_cases.append('')
        
        return test_cases
    
    def _generate_error_tests(self, func: Dict) -> List[str]:
        """Generate error handling tests for a function.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of test case code lines.
        """
        func_name = func.get('name', 'unknown')
        
        test_cases = []
        
        # Test that function raises appropriate exceptions
        test_cases.append(f'def test_{func_name}_raises_on_invalid_input():')
        test_cases.append(f'    # Test that function raises appropriate exceptions')
        test_cases.append(f'    with pytest.raises((ValueError, TypeError)):')
        test_cases.append(f'        {func_name}(invalid_input)')
        test_cases.append('')
        
        return test_cases
    
    def _generate_class_tests(self, classes: List[Dict], output_path: Path) -> str:
        """Generate unit tests for classes.
        
        Args:
            classes: List of class information.
            output_path: Path to output directory.
            
        Returns:
            Path to generated test file.
        """
        test_file = output_path / "test_classes.py"
        
        test_content = []
        test_content.append('"""Unit tests for classes."""')
        test_content.append('')
        test_content.append('import pytest')
        test_content.append('from unittest.mock import Mock, patch, MagicMock')
        test_content.append('')
        
        for cls in classes:
            test_content.extend(self._generate_class_test_cases(cls))
            test_content.append('')
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write('\n'.join(test_content))
        
        return str(test_file)
    
    def _generate_class_test_cases(self, cls: Dict) -> List[str]:
        """Generate test cases for a single class.
        
        Args:
            cls: Class information dictionary.
            
        Returns:
            List of test case code lines.
        """
        class_name = cls.get('name', 'unknown')
        
        test_cases = []
        
        # Skip private classes
        if class_name.startswith('_'):
            return test_cases
        
        # Import statement
        test_cases.append(f'# Tests for {class_name}')
        test_cases.append('')
        
        # Test initialization
        test_cases.append(f'def test_{class_name}_init():')
        test_cases.append(f'    # Test class initialization')
        test_cases.append(f'    # instance = {class_name}()')
        test_cases.append(f'    # Add your assertions')
        test_cases.append('')
        
        # Test methods
        methods = cls.get('methods', [])
        for method in methods:
            method_name = method.get('name', '')
            
            # Skip private methods
            if method_name.startswith('_') and not method_name.startswith('__'):
                continue
            
            test_cases.extend(self._generate_method_tests(class_name, method))
        
        return test_cases
    
    def _generate_method_tests(self, class_name: str, method: Dict) -> List[str]:
        """Generate test cases for a class method.
        
        Args:
            class_name: Name of the class.
            method: Method information dictionary.
            
        Returns:
            List of test case code lines.
        """
        method_name = method.get('name', 'unknown')
        args = method.get('args', [])
        
        test_cases = []
        
        # Skip init
        if method_name == '__init__':
            return test_cases
        
        # Test method
        test_cases.append(f'def test_{class_name}_{method_name}():')
        
        # Skip self in args
        test_args = args[1:] if args else []
        
        if test_args:
            test_inputs = []
            for arg in test_args:
                arg_type = arg.get('annotation', '')
                test_input = self._get_test_value_for_type(arg_type)
                test_inputs.append(test_input)
            
            call_args = ', '.join(test_inputs)
            
            if method.get('is_static') or method.get('is_classmethod'):
                test_cases.append(f'    # Test {method_name} method')
                test_cases.append(f'    # result = {class_name}.{method_name}({call_args})')
            else:
                test_cases.append(f'    # Test {method_name} method')
                test_cases.append(f'    # instance = {class_name}()')
                test_cases.append(f'    # result = instance.{method_name}({call_args})')
        else:
            if method.get('is_static') or method.get('is_classmethod'):
                test_cases.append(f'    # Test {method_name} method')
                test_cases.append(f'    # result = {class_name}.{method_name}()')
            else:
                test_cases.append(f'    # Test {method_name} method')
                test_cases.append(f'    # instance = {class_name}()')
                test_cases.append(f'    # result = instance.{method_name}()')
        
        test_cases.append(f'    # Add your assertions')
        test_cases.append('')
        
        return test_cases
    
    def _get_test_value_for_type(self, type_hint: str) -> str:
        """Get a test value for a given type hint.
        
        Args:
            type_hint: The type hint string.
            
        Returns:
            A test value as a string.
        """
        type_mapping = {
            'int': '1',
            'float': '1.0',
            'str': '"test"',
            'bool': 'True',
            'list': '[]',
            'List': '[]',
            'dict': '{}',
            'Dict': '{}',
            'set': 'set()',
            'Set': 'set()',
            'tuple': '()',
            'Tuple': '()',
            'bytes': 'b""',
            'bytearray': 'bytearray()',
            'MemoryView': 'memoryview(b"")',
            'None': 'None',
            'Optional': 'None',
            'Any': 'None'
        }
        
        # Handle Optional types
        if 'Optional[' in type_hint:
            return 'None'
        
        # Handle List/Dict with generics
        if 'List[' in type_hint:
            return '[]'
        if 'Dict[' in type_hint:
            return '{}'
        
        return type_mapping.get(type_hint, 'None')
