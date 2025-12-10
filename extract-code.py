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


def ensure_shebang(code: str, language: str = None) -> str:
    """
    Ensure code has a valid shebang line at the beginning.

    Args:
        code: Source code to check
        language: Programming language (python, bash, javascript, etc.)

    Returns:
        Code with shebang line if missing
    """
    lines = code.split('\n')

    # Check if first line is already a shebang
    if lines and lines[0].strip().startswith('#!'):
        return code

    # Detect language if not specified
    if not language:
        if 'import ' in code or 'def ' in code or 'class ' in code:
            language = 'python'
        elif 'function ' in code or 'const ' in code or 'let ' in code:
            language = 'javascript'
        elif 'echo ' in code or '[[' in code or 'if [' in code:
            language = 'bash'

    # Determine appropriate shebang based on language
    shebang = None
    if language in ['python', 'py']:
        shebang = '#!/usr/bin/env python3'
    elif language in ['bash', 'sh', 'shell']:
        shebang = '#!/bin/bash'
    elif language in ['javascript', 'js', 'node']:
        shebang = '#!/usr/bin/env node'
    elif language in ['ruby', 'rb']:
        shebang = '#!/usr/bin/env ruby'
    elif language in ['perl', 'pl']:
        shebang = '#!/usr/bin/env perl'
    elif language in ['php']:
        shebang = '#!/usr/bin/env php'

    # Insert shebang if determined
    if shebang:
        return f"{shebang}\n{code}"

    return code


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


def extract_code_blocks(text: str, language: str = None) -> tuple:
    """
    Extract code blocks from markdown-formatted text.

    Args:
        text: Input text containing markdown code blocks
        language: Optional language filter (e.g., 'python', 'bash')

    Returns:
        Tuple of (extracted code content, detected language)
    """
    # Pattern matches ```language\ncode\n``` blocks
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        # No code blocks found, return original text
        return (text, language)

    # Filter by language if specified
    if language:
        matches = [(lang, code) for lang, code in matches if lang.lower() == language.lower()]

    if not matches:
        sys.stderr.write(f"No code blocks found for language: {language}\n")
        return ("", language)

    # Return the first matching code block and its language
    detected_lang, code = matches[0]
    return (code.strip(), detected_lang or language)


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
        detected_lang = args.lang
    else:
        code, detected_lang = extract_code_blocks(text, args.lang)

    # Ensure shebang is present
    code = ensure_shebang(code, detected_lang)

    # Strip comments if requested
    if args.strip_comments:
        code = strip_comments(code, detected_lang)

    print(code)


if __name__ == "__main__":
    main()
