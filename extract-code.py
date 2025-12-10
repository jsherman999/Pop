#!/usr/bin/env python3
"""
Extract code blocks from markdown output (e.g., from LLM responses).

Usage:
    ollama run gpt-oss "write a python script..." | extract-code.py > script.py
    ollama run gpt-oss "write a bash script..." | extract-code.py --lang bash > script.sh
    ollama run gpt-oss "write a python script..." | extract-code.py --strip-comments > script.py
"""

import argparse
import sys
import re
import ast


def strip_comments(code: str, language: str = None) -> str:
    """
    Remove comments from code while preserving functionality.

    Args:
        code: Source code to strip comments from
        language: Programming language (python, bash, javascript, etc.)

    Returns:
        Code with comments removed
    """
    if not language:
        # Try to detect language from code
        if code.strip().startswith('#!/usr/bin/env python') or 'import ' in code or 'def ' in code:
            language = 'python'
        elif code.strip().startswith('#!/bin/bash') or code.strip().startswith('#!/bin/sh'):
            language = 'bash'

    if language in ['python', 'py']:
        # Remove # comments (but preserve shebangs)
        lines = code.split('\n')
        cleaned_lines = []
        for i, line in enumerate(lines):
            # Keep shebang on first line
            if i == 0 and line.strip().startswith('#!'):
                cleaned_lines.append(line)
            else:
                # Remove inline comments
                # Handle strings to avoid removing # in strings
                if '#' in line:
                    # Simple approach: remove # comments not in strings
                    # More robust would use tokenizer, but this handles most cases
                    in_string = False
                    quote_char = None
                    result = []
                    for j, char in enumerate(line):
                        if char in ['"', "'"] and (j == 0 or line[j-1] != '\\'):
                            if not in_string:
                                in_string = True
                                quote_char = char
                            elif char == quote_char:
                                in_string = False
                        if char == '#' and not in_string:
                            break
                        result.append(char)
                    cleaned_lines.append(''.join(result).rstrip())
                else:
                    cleaned_lines.append(line)

        code = '\n'.join(cleaned_lines)

        # Remove docstrings (""" and ''')
        code = re.sub(r'^\s*""".*?"""\s*$', '', code, flags=re.MULTILINE | re.DOTALL)
        code = re.sub(r"^\s*'''.*?'''\s*$", '', code, flags=re.MULTILINE | re.DOTALL)

    elif language in ['bash', 'sh', 'shell']:
        # Remove # comments (but preserve shebangs)
        lines = code.split('\n')
        cleaned_lines = []
        for i, line in enumerate(lines):
            # Keep shebang on first line
            if i == 0 and line.strip().startswith('#!'):
                cleaned_lines.append(line)
            else:
                # Remove # comments
                if '#' in line:
                    # Simple approach for bash
                    idx = line.find('#')
                    cleaned_lines.append(line[:idx].rstrip())
                else:
                    cleaned_lines.append(line)
        code = '\n'.join(cleaned_lines)

    elif language in ['javascript', 'js', 'typescript', 'ts']:
        # Remove // comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        # Remove /* */ comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    # Remove excessive blank lines (more than 2 consecutive)
    code = re.sub(r'\n\s*\n\s*\n+', '\n\n', code)

    return code


def extract_code_blocks(text: str, language: str = None) -> str:
    """
    Extract code blocks from markdown-formatted text.

    Args:
        text: Input text containing markdown code blocks
        language: Optional language filter (e.g., 'python', 'bash')

    Returns:
        Extracted code content
    """
    # Pattern matches ```language\ncode\n``` blocks
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        # No code blocks found, return original text
        return text

    # Filter by language if specified
    if language:
        matches = [(lang, code) for lang, code in matches if lang.lower() == language.lower()]

    if not matches:
        sys.stderr.write(f"No code blocks found for language: {language}\n")
        return ""

    # Return the first matching code block
    return matches[0][1].strip()


def main():
    parser = argparse.ArgumentParser(
        description="Extract code blocks from markdown text."
    )
    parser.add_argument(
        "-l", "--lang",
        help="Filter by language (e.g., python, bash, javascript)"
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Extract all code blocks (concatenated)"
    )
    parser.add_argument(
        "-s", "--strip-comments",
        action="store_true",
        help="Remove comments from extracted code"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input file (default: stdin)"
    )

    args = parser.parse_args()

    # Read input
    if args.input:
        with open(args.input) as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Extract code
    if args.all:
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        if args.lang:
            matches = [(lang, code) for lang, code in matches if lang.lower() == args.lang.lower()]
        code = '\n\n'.join(code.strip() for _, code in matches)
    else:
        code = extract_code_blocks(text, args.lang)

    # Strip comments if requested
    if args.strip_comments:
        code = strip_comments(code, args.lang)

    print(code)


if __name__ == "__main__":
    main()
