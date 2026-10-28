"""Certificado conservador de restricciones de OpenCode.

Lee la salida de `opencode debug config --standalone` y comprueba que la
configuración efectiva acredita dos bloqueos: el proveedor directo `openai` y
la subdelegación interna mediante la herramienta `subagent`.

El certificado es deliberadamente conservador: si cualquier regla `allow` puede
solaparse con un bloqueo, no se acredita nada. No reimplementa la precedencia de
OpenCode, que depende del origen de cada regla y del orden de lectura; calcula
solo si un permiso podría contradecir el bloqueo exigido.

Fuentes oficiales:
https://dev.opencode.ai/v2/docs/policies/ y
https://dev.opencode.ai/v2/docs/config/
"""

from __future__ import annotations

import re
from typing import Any

DENIED_PROVIDER = "openai"
DENIED_TOOL = "subagent:*"
ACTIONS = frozenset({"provider.use", "tool.use", "integration.use"})
EFFECTS = frozenset({"allow", "deny"})
RULE_KEYS = frozenset({"action", "resource", "effect"})
SOURCE_TYPES = frozenset({"document", "directory"})


def _wildcard_regex(pattern: str) -> str:
    """Traduce los únicos comodines de OpenCode: `*` y `?` sobre todo el valor.

    No se usa `fnmatch`: los corchetes no son comodines en OpenCode.
    """

    return re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")


def _pattern_matches(pattern: str, value: str) -> bool:
    """Indica si el patrón casa el valor según las reglas de OpenCode.

    `*` casa cero o más caracteres y `?` casa uno, sobre el valor entero. Un
    patrón terminado en ` *` también casa el valor sin argumentos, como
    documenta OpenCode para `shell:git push *`.
    """

    if pattern.endswith(" *"):
        base = pattern[:-1]
        if re.fullmatch(_wildcard_regex(base.rstrip()), value) is not None:
            return True
        return re.fullmatch(_wildcard_regex(base) + ".*", value) is not None
    return re.fullmatch(_wildcard_regex(pattern), value) is not None


def _provider_allow_overlaps(resource: str) -> bool:
    """Un `allow` de proveedor solapa si el patrón casa el literal `openai`."""

    return _pattern_matches(resource, DENIED_PROVIDER)


def _tool_allow_is_disjoint(resource: str) -> bool:
    """Indica si un `allow` de herramienta no puede tocar `subagent:*`.

    El bloqueo usa un comodín, así que la disjunción solo puede probarse cuando
    el prefijo literal antes de `:` es distinto del del bloqueo. Con comodines en
    el prefijo o sin `:` el patrón es ambiguo y se rechaza.
    """

    if ":" not in resource:
        return False
    prefix = resource.split(":", 1)[0]
    if "*" in prefix or "?" in prefix:
        return False
    return prefix != DENIED_TOOL.split(":", 1)[0]


def _parse_rule(item: object) -> dict[str, str] | None:
    """Normaliza una regla; devuelve `None` si el formato no es válido."""

    if not isinstance(item, dict):
        return None
    if set(item) != RULE_KEYS:
        return None
    action = item["action"]
    resource = item["resource"]
    effect = item["effect"]
    if not isinstance(action, str) or not isinstance(resource, str):
        return None
    if not isinstance(effect, str):
        return None
    if action not in ACTIONS or effect not in EFFECTS:
        return None
    return {"action": action, "resource": resource, "effect": effect}


def _collect_rules(info: dict[str, Any]) -> list[dict[str, str]] | None:
    """Recoge `policies` y `experimental.policies`; `None` si algo es inválido.

    Se distingue la ausencia de la clave de un valor `null`: un `null` en
    `policies`, `experimental` o `experimental.policies` invalida el
    certificado, porque la configuración efectiva no es interpretable.
    """

    groups: list[object] = []
    if "policies" in info:
        policies = info["policies"]
        if policies is None:
            return None
        groups.append(policies)
    if "experimental" in info:
        experimental = info["experimental"]
        if experimental is None or not isinstance(experimental, dict):
            return None
        if "policies" in experimental:
            inherited = experimental["policies"]
            if inherited is None:
                return None
            groups.append(inherited)

    collected: list[dict[str, str]] = []
    for group in groups:
        if not isinstance(group, list):
            return None
        for item in group:
            parsed = _parse_rule(item)
            if parsed is None:
                return None
            collected.append(parsed)
    return collected


def _source_rules(source: object) -> list[dict[str, str]] | None:
    """Extrae las reglas de una fuente conocida; `None` si el formato falla.

    Solo se aceptan las fuentes `document` con su objeto `info` y `directory`
    sin `info`. Cualquier otro formato se considera desconocido.
    """

    if not isinstance(source, dict):
        return None
    source_type = source.get("type")
    if not isinstance(source_type, str) or source_type not in SOURCE_TYPES:
        return None
    if source_type == "directory":
        if "info" in source:
            return None
        return []
    info = source.get("info")
    if not isinstance(info, dict):
        return None
    return _collect_rules(info)


def _is_certified(rules: list[dict[str, str]]) -> bool:
    """Exige los dos bloqueos exactos y ningún `allow` que pueda solaparlos."""

    provider_denied = any(
        rule["action"] == "provider.use"
        and rule["resource"] == DENIED_PROVIDER
        and rule["effect"] == "deny"
        for rule in rules
    )
    tool_denied = any(
        rule["action"] == "tool.use"
        and rule["resource"] == DENIED_TOOL
        and rule["effect"] == "deny"
        for rule in rules
    )
    if not provider_denied or not tool_denied:
        return False

    for rule in rules:
        if rule["effect"] != "allow":
            continue
        if rule["action"] == "provider.use" and _provider_allow_overlaps(
            rule["resource"]
        ):
            return False
        if rule["action"] == "tool.use" and not _tool_allow_is_disjoint(
            rule["resource"]
        ):
            return False
    return True


def configuration_is_restricted(payload: object) -> bool:
    """Indica si la configuración efectiva acredita los bloqueos exigidos.

    `payload` es la lista de fuentes devuelta por
    `opencode debug config --standalone`. Una lista vacía, un formato
    desconocido o una regla malformada impiden la certificación.
    """

    if not isinstance(payload, list) or not payload:
        return False
    rules: list[dict[str, str]] = []
    for source in payload:
        collected = _source_rules(source)
        if collected is None:
            return False
        rules.extend(collected)
    return _is_certified(rules)
