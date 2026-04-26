# =============================================================================
# DSL Parser — Parse emergency protocol DSL using Lark
# =============================================================================
from __future__ import annotations

import os
from pathlib import Path

from lark import Lark, Tree, UnexpectedInput


class DSLParser:
    """Parse emergency protocol DSL text into structured protocol trees."""

    def __init__(self):
        grammar_path = Path(__file__).parent.parent / "grammar" / "emergency.lark"
        with open(grammar_path) as f:
            grammar = f.read()

        self._parser = Lark(
            grammar,
            parser="lalr",
            start="start",
        )

    def parse(self, dsl_text: str) -> Tree:
        """Parse DSL text into a Lark parse tree.

        Args:
            dsl_text: Emergency protocol DSL source code

        Returns:
            Lark Tree object

        Raises:
            SyntaxError: If DSL text has invalid syntax
        """
        try:
            return self._parser.parse(dsl_text)
        except UnexpectedInput as e:
            raise SyntaxError(
                f"DSL syntax error at line {e.line}, column {e.column}: "
                f"Unexpected {e.__class__.__name__}"
            )

    def validate(self, dsl_text: str) -> dict:
        """Validate DSL syntax without executing.

        Returns:
            Dict with 'valid' boolean and optional 'error' message
        """
        try:
            tree = self.parse(dsl_text)
            protocols = [child for child in tree.children if child.data == "protocol"]
            return {
                "valid": True,
                "protocol_count": len(protocols),
                "tree": tree.pretty(),
            }
        except SyntaxError as e:
            return {"valid": False, "error": str(e)}

    def extract_protocols(self, dsl_text: str) -> list[dict]:
        """Parse DSL and extract structured protocol definitions."""
        tree = self.parse(dsl_text)
        protocols = []

        for child in tree.children:
            if child.data == "protocol":
                protocol = self._extract_protocol(child)
                protocols.append(protocol)

        return protocols

    def _extract_protocol(self, node: Tree) -> dict:
        """Extract a single protocol definition from parse tree."""
        trigger = None
        conditions = []
        actions = []

        for child in node.children:
            if child.data == "trigger":
                trigger = str(child.children[0])
            elif child.data == "condition":
                cond_type = str(child.children[0])
                cond_value = str(child.children[1]) if len(child.children) > 1 else None
                conditions.append({"type": cond_type, "value": cond_value})
            elif child.data.endswith("_action"):
                action_type = child.data.replace("_action", "")
                target = str(child.children[0]).strip('"')
                actions.append({"type": action_type, "target": target})

        return {
            "trigger": trigger,
            "conditions": conditions,
            "actions": actions,
        }
