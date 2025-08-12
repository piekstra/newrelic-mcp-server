"""
Log Parsing Rule Management for New Relic

This module provides functionality for creating, updating, deleting, and testing
log parsing rules in New Relic, including intelligent GROK pattern generation.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def generate_grok_pattern_for_log(log_sample: str) -> Tuple[str, str]:
    """
    Generate a GROK pattern from a single log sample by identifying known patterns
    This is an improved version that handles your log format better
    """
    grok_pattern = log_sample
    nrql_pattern = log_sample

    # Replace UUIDs
    uuid_pattern = re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    )
    for match in uuid_pattern.finditer(log_sample):
        uuid_str = match.group()
        # Determine context for field name
        before_text = log_sample[: match.start()].rstrip()
        if "user" in before_text.lower()[-20:]:
            field_name = "user_id"
        else:
            field_name = "uuid"

        grok_pattern = grok_pattern.replace(
            uuid_str, f"%{{UUID:{field_name}:string}}", 1
        )
        nrql_pattern = nrql_pattern.replace(uuid_str, "%", 1)

    # Replace email addresses
    email_pattern = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
    for match in email_pattern.finditer(log_sample):
        email_str = match.group()
        grok_pattern = grok_pattern.replace(email_str, "%{DATA:email:string}", 1)
        nrql_pattern = nrql_pattern.replace(email_str, "%", 1)

    # Replace integers in specific contexts (e.g., "updated X rows")
    # Look for patterns like "updated N rows, expected M"
    rows_pattern = re.compile(
        r"(updated|deleted|inserted|affected)\s+(\d+)\s+rows?,\s+expected\s+(\d+)"
    )
    for match in rows_pattern.finditer(log_sample):
        full_match = match.group()
        action = match.group(1)

        replacement = f"{action} %{{INT:rows_affected:long}} rows, expected %{{INT:rows_expected:long}}"
        grok_pattern = grok_pattern.replace(full_match, replacement, 1)
        nrql_pattern = nrql_pattern.replace(
            full_match, f"{action} % rows, expected %", 1
        )

    # Replace boolean values in key-value pairs
    bool_pattern = re.compile(r"(\w+)\s+(True|False|true|false)")
    for match in bool_pattern.finditer(log_sample):
        full_match = match.group()
        key = match.group(1)

        # Convert key to snake_case field name
        field_name = key.lower()

        replacement = f"{key} %{{WORD:{field_name}:string}}"
        grok_pattern = grok_pattern.replace(full_match, replacement, 1)
        nrql_pattern = nrql_pattern.replace(full_match, f"{key} %", 1)

    # Replace name patterns (FirstName X, LastName Y)
    name_pattern = re.compile(r"(FirstName|LastName)\s+([A-Za-z]+)")
    for match in name_pattern.finditer(log_sample):
        full_match = match.group()
        label = match.group(1)

        field_name = "first_name" if label == "FirstName" else "last_name"
        replacement = f"{label} %{{WORD:{field_name}:string}}"
        grok_pattern = grok_pattern.replace(full_match, replacement, 1)
        nrql_pattern = nrql_pattern.replace(full_match, f"{label} %", 1)

    # Escape special regex characters for GROK
    # Parentheses need to be escaped
    grok_pattern = grok_pattern.replace("(", "\(").replace(")", "\)")

    return grok_pattern, nrql_pattern


class GrokPatternGenerator:
    """Generates GROK patterns from log samples"""

    COMMON_PATTERNS = {
        # Basic patterns
        "WORD": r"[A-Za-z0-9_-]+",
        "INT": r"[0-9]+",
        "NUMBER": r"[0-9]+(?:\.[0-9]+)?",
        "GREEDYDATA": r".*",
        "DATA": r".*?",
        "SPACE": r"\s+",
        "NOTSPACE": r"\S+",
        # Common log patterns
        "TIMESTAMP_ISO8601": r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?",
        "LOGLEVEL": r"(?:DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|TRACE)",
        "UUID": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        "IPV4": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "HOSTNAME": r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",
        "PATH": r"(?:/[^/\s]*)+",
        "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "URL": r"https?://[^\s]+",
        "JAVACLASS": r"(?:[a-zA-Z_][a-zA-Z0-9_]*\.)*[a-zA-Z_][a-zA-Z0-9_]*",
        "JAVAMETHOD": r"[a-zA-Z_][a-zA-Z0-9_]*",
        "JAVAFILE": r"[a-zA-Z_][a-zA-Z0-9_]*\.java",
        "QUOTEDSTRING": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
    }

    def analyze_log_samples(self, samples: List[str]) -> Dict[str, Any]:
        """
        Analyze log samples to identify common patterns and extractable fields
        """
        analysis = {
            "common_prefix": self._find_common_prefix(samples),
            "common_suffix": self._find_common_suffix(samples),
            "variable_parts": [],
            "suggested_fields": [],
            "patterns_found": [],
        }

        # Find variable parts between samples
        if len(samples) > 1:
            analysis["variable_parts"] = self._find_variable_parts(samples)

        # Detect common patterns in the logs
        for sample in samples:
            # Check for timestamps
            if re.search(self.COMMON_PATTERNS["TIMESTAMP_ISO8601"], sample):
                analysis["patterns_found"].append("timestamp")

            # Check for log levels
            if re.search(self.COMMON_PATTERNS["LOGLEVEL"], sample):
                analysis["patterns_found"].append("loglevel")

            # Check for UUIDs
            if re.search(self.COMMON_PATTERNS["UUID"], sample):
                analysis["patterns_found"].append("uuid")

            # Check for IPs
            if re.search(self.COMMON_PATTERNS["IPV4"], sample):
                analysis["patterns_found"].append("ipv4")

            # Check for URLs
            if re.search(self.COMMON_PATTERNS["URL"], sample):
                analysis["patterns_found"].append("url")

            # Check for Java stack traces
            if (
                re.search(self.COMMON_PATTERNS["JAVACLASS"], sample)
                and "Exception" in sample
            ):
                analysis["patterns_found"].append("java_stacktrace")

            # Check for numeric values (potential metrics)
            numbers = re.findall(r"\b\d+(?:\.\d+)?\b", sample)
            if numbers:
                analysis["patterns_found"].append("numeric_values")

        return analysis

    def _find_common_prefix(self, samples: List[str]) -> str:
        """Find the longest common prefix among samples"""
        if not samples:
            return ""

        prefix = samples[0]
        for sample in samples[1:]:
            while not sample.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix

    def _find_common_suffix(self, samples: List[str]) -> str:
        """Find the longest common suffix among samples"""
        if not samples:
            return ""

        suffix = samples[0]
        for sample in samples[1:]:
            while not sample.endswith(suffix):
                suffix = suffix[1:]
                if not suffix:
                    return ""
        return suffix

    def _find_variable_parts(self, samples: List[str]) -> List[Dict[str, Any]]:
        """Identify parts that vary between samples"""
        if len(samples) < 2:
            return []

        variable_parts = []

        # Simple approach: find differences between first two samples
        s1, s2 = samples[0], samples[1]

        # Find all differences
        import difflib

        matcher = difflib.SequenceMatcher(None, s1, s2)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "replace":
                part1 = s1[i1:i2]
                part2 = s2[j1:j2]

                # Try to identify what type of data this is
                field_type = self._identify_field_type(part1, part2)

                variable_parts.append(
                    {
                        "position": i1,
                        "sample_values": [part1, part2],
                        "suggested_type": field_type,
                    }
                )

        return variable_parts

    def _identify_field_type(self, val1: str, val2: str) -> str:
        """Identify the type of field based on sample values"""
        # Check if numeric
        if val1.isdigit() and val2.isdigit():
            return "INT"

        try:
            float(val1)
            float(val2)
            return "NUMBER"
        except ValueError:
            pass

        # Check if UUID
        uuid_pattern = re.compile(
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
        if uuid_pattern.match(val1) and uuid_pattern.match(val2):
            return "UUID"

        # Check if looks like an ID (alphanumeric)
        if re.match(r"^[A-Za-z0-9_-]+$", val1) and re.match(r"^[A-Za-z0-9_-]+$", val2):
            if len(val1) == len(val2):
                return "ID"
            return "WORD"

        # Default to GREEDYDATA for complex strings
        return "GREEDYDATA"

    def generate_grok_pattern(
        self, samples: List[str], field_hints: Optional[Dict[str, str]] = None
    ) -> Tuple[str, str]:
        """
        Generate a GROK pattern from log samples

        Returns:
            Tuple of (grok_pattern, nrql_like_pattern)
        """
        if not samples:
            return "", ""

        analysis = self.analyze_log_samples(samples)

        # Start with the first sample as a template
        template = samples[0]
        grok_pattern = re.escape(template)
        nrql_pattern = template

        # Replace variable parts with GROK patterns
        for var_part in sorted(
            analysis["variable_parts"], key=lambda x: x["position"], reverse=True
        ):
            pos = var_part["position"]
            sample_val = var_part["sample_values"][0]
            field_type = var_part["suggested_type"]

            # Generate field name from context or use generic name
            field_name = self._generate_field_name(template, pos, field_type)

            # Apply field hints if provided
            if field_hints and field_name in field_hints:
                field_type = field_hints[field_name]

            # Create the GROK capture group
            if field_type == "INT":
                grok_replacement = f"%{{INT:{field_name}:long}}"
            elif field_type == "NUMBER":
                grok_replacement = f"%{{NUMBER:{field_name}:float}}"
            elif field_type == "UUID":
                grok_replacement = f"%{{UUID:{field_name}:string}}"
            elif field_type == "WORD":
                grok_replacement = f"%{{WORD:{field_name}:string}}"
            elif field_type == "ID":
                grok_replacement = f"%{{NOTSPACE:{field_name}:string}}"
            else:
                grok_replacement = f"%{{GREEDYDATA:{field_name}:string}}"

            # Replace in the pattern
            escaped_val = re.escape(sample_val)
            grok_pattern = (
                grok_pattern[:pos]
                + grok_replacement
                + grok_pattern[pos + len(escaped_val) :]
            )

            # Create NRQL LIKE pattern
            nrql_pattern = (
                nrql_pattern[:pos] + "%" + nrql_pattern[pos + len(sample_val) :]
            )

        # Unescape the static parts for readability
        # grok_pattern = grok_pattern.replace("\\", "")

        return grok_pattern, nrql_pattern

    def _generate_field_name(
        self, template: str, position: int, field_type: str
    ) -> str:
        """Generate a meaningful field name based on context"""
        # Look at surrounding words for context
        before = template[:position].split()[-1] if position > 0 else ""
        after = template[position:].split()[0] if position < len(template) else ""

        # Common patterns
        if (
            "time" in before.lower()
            or "duration" in before.lower()
            or "ms" in after.lower()
        ):
            return "duration_ms" if "ms" in after else "timestamp"
        elif "id" in before.lower() or "id" in after.lower():
            return (
                before.lower().replace(":", "").replace("-", "_") + "_id"
                if before
                else "id"
            )
        elif "user" in before.lower():
            return "user_id"
        elif "account" in before.lower():
            return "account_id"
        elif "company" in before.lower():
            return "company_id"
        elif "bytes" in after.lower():
            return "bytes"
        elif field_type == "INT" or field_type == "NUMBER":
            return "value"
        elif field_type == "UUID":
            return "uuid"
        else:
            return "field"


async def list_log_parsing_rules(client, account_id: str) -> List[Dict[str, Any]]:
    """List all log parsing rules for an account"""
    query = """
    query($accountId: Int!) {
        actor {
            account(id: $accountId) {
                logConfigurations {
                    parsingRules {
                        accountId
                        deleted
                        description
                        enabled
                        grok
                        id
                        lucene
                        nrql
                        updatedAt
                        createdBy {
                            email
                            name
                        }
                    }
                }
            }
        }
    }
    """

    variables = {"accountId": int(account_id)}
    result = await client.nerdgraph_query(query, variables)

    if result and "data" in result:
        account_data = result["data"].get("actor", {}).get("account", {})
        if account_data and "logConfigurations" in account_data:
            rules = account_data["logConfigurations"].get("parsingRules", [])
            return [r for r in rules if r and not r.get("deleted", False)]

    return []


async def create_log_parsing_rule(
    client,
    account_id: str,
    description: str,
    grok: str,
    nrql: str,
    enabled: bool = True,
    lucene: str = "",
) -> Dict[str, Any]:
    """Create a new log parsing rule"""
    # Escape special characters in GROK pattern for GraphQL
    # grok_escaped = grok.replace("\\", "\\\\")

    mutation = f"""
    mutation {{
        logConfigurationsCreateParsingRule(
            accountId: {int(account_id)},
            rule: {{
                description: "{description}"
                enabled: {str(enabled).lower()}
                grok: "{grok}"
                lucene: "{lucene}"
                nrql: "{nrql}"
            }}
        ) {{
            rule {{
                id
                description
                enabled
                grok
                lucene
                nrql
                updatedAt
            }}
            errors {{
                message
                type
            }}
        }}
    }}
    """

    result = await client.nerdgraph_query(mutation)

    if result and "data" in result:
        create_result = result["data"].get("logConfigurationsCreateParsingRule", {})
        if create_result.get("errors"):
            raise Exception(f"Failed to create rule: {create_result['errors']}")
        return create_result.get("rule", {})

    raise Exception("Failed to create parsing rule")


async def update_log_parsing_rule(
    client,
    account_id: str,
    rule_id: str,
    description: Optional[str] = None,
    grok: Optional[str] = None,
    nrql: Optional[str] = None,
    enabled: Optional[bool] = None,
    lucene: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing log parsing rule"""

    # Build the update fields
    rule_fields = []
    if description is not None:
        rule_fields.append(f'description: "{description}"')
    if enabled is not None:
        rule_fields.append(f"enabled: {str(enabled).lower()}")
    if grok is not None:
        # grok_escaped = grok.replace("\\", "\\\\")
        rule_fields.append(f'grok: "{grok}"')
    if lucene is not None:
        rule_fields.append(f'lucene: "{lucene}"')
    if nrql is not None:
        rule_fields.append(f'nrql: "{nrql}"')

    rule_object = "{ " + ", ".join(rule_fields) + " }"

    mutation = f"""
    mutation {{
        logConfigurationsUpdateParsingRule(
            accountId: {int(account_id)},
            id: "{rule_id}",
            rule: {rule_object}
        ) {{
            rule {{
                id
                description
                enabled
                grok
                lucene
                nrql
                updatedAt
            }}
            errors {{
                message
                type
            }}
        }}
    }}
    """

    result = await client.nerdgraph_query(mutation)

    if result and "data" in result:
        update_result = result["data"].get("logConfigurationsUpdateParsingRule", {})
        if update_result.get("errors"):
            raise Exception(f"Failed to update rule: {update_result['errors']}")
        return update_result.get("rule", {})

    raise Exception("Failed to update parsing rule")


async def delete_log_parsing_rule(client, account_id: str, rule_id: str) -> bool:
    """Delete a log parsing rule"""
    mutation = f"""
    mutation {{
        logConfigurationsDeleteParsingRule(
            accountId: {int(account_id)},
            id: "{rule_id}"
        ) {{
            errors {{
                message
                type
            }}
        }}
    }}
    """

    result = await client.nerdgraph_query(mutation)

    if result and "data" in result:
        delete_result = result["data"].get("logConfigurationsDeleteParsingRule", {})
        if delete_result.get("errors"):
            raise Exception(f"Failed to delete rule: {delete_result['errors']}")
        return True

    return False


async def test_log_parsing_rule(
    client, account_id: str, log_samples: List[str], grok_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test a log parsing rule against sample logs
    If no grok_pattern is provided, it will generate one automatically
    """
    generator = GrokPatternGenerator()

    if not grok_pattern:
        # Generate pattern from samples
        grok_pattern, nrql_pattern = generator.generate_grok_pattern(log_samples)
    else:
        # Generate NRQL pattern from existing GROK
        nrql_pattern = grok_pattern
        # Simple conversion - replace GROK patterns with %
        nrql_pattern = re.sub(r"%\{[^}]+\}", "%", nrql_pattern)

    # Test the pattern by querying logs
    test_query = f"""
    SELECT count(*) as matching_logs
    FROM Log
    WHERE message LIKE '{nrql_pattern}'
    SINCE 1 hour ago
    """

    result = await client.query_nrql(account_id, test_query)

    return {
        "grok_pattern": grok_pattern,
        "nrql_pattern": nrql_pattern,
        "test_results": result,
        "sample_count": len(log_samples),
    }


async def generate_parsing_rule_from_logs(
    client,
    account_id: str,
    log_query: Optional[str] = None,
    log_samples: Optional[List[str]] = None,
    time_range: str = "1 hour ago",
    field_hints: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Generate a log parsing rule from either a query or provided samples

    Args:
        client: New Relic client
        account_id: Account ID
        log_query: Optional NRQL query to fetch logs
        log_samples: Optional list of log message samples
        time_range: Time range for log query (default: "1 hour ago")
        field_hints: Optional hints for field types

    Returns:
        Dict containing the generated GROK pattern, NRQL pattern, and analysis
    """
    samples = log_samples or []

    # If no samples provided, fetch from New Relic
    if not samples and log_query:
        query = f"""
        SELECT message
        FROM Log
        WHERE {log_query}
        SINCE {time_range}
        LIMIT 10
        """

        result = await client.query_nrql(account_id, query)

        if result and "results" in result:
            samples = [
                r.get("message", "") for r in result["results"] if r.get("message")
            ]

    if not samples:
        raise ValueError("No log samples available to generate pattern")

    # Use improved pattern generation for single samples
    if len(samples) == 1:
        grok_pattern, nrql_pattern = generate_grok_pattern_for_log(samples[0])
        # Create a simple analysis for single sample
        analysis = {"patterns_found": [], "samples_analyzed": 1}
        suggested_desc = "Auto-generated parsing rule for single log sample"
    else:
        generator = GrokPatternGenerator()
        analysis = generator.analyze_log_samples(samples)
        grok_pattern, nrql_pattern = generator.generate_grok_pattern(
            samples, field_hints
        )
        suggested_desc = (
            f"Auto-generated parsing rule for {analysis['patterns_found']}"
            if analysis["patterns_found"]
            else "Auto-generated parsing rule"
        )

    return {
        "grok_pattern": grok_pattern,
        "nrql_pattern": f"SELECT * FROM Log WHERE message LIKE '{nrql_pattern}'",
        "analysis": analysis,
        "samples_used": len(samples),
        "suggested_description": suggested_desc,
    }
