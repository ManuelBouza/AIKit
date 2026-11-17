"""Lee tickets locales sin modificar el registro ni conceder permisos."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any, NoReturn
from urllib.parse import urlsplit

import mistune

PHASES = (
    "pendiente",
    "en_curso",
    "en_revision",
    "pendiente_integracion",
    "finalizada",
    "cancelada",
)
ATTENTION = ("normal", "esperando_usuario", "bloqueada", "pausada")
FIELDS = set(
    "schemaVersion id projectId titulo creada actualizada ideas origen responsable chat fase atencion motivo siguienteAccion autorizacion dependencias referencias".split()
)
SECTIONS = ("Resultado", "Alcance", "Exclusiones", "Aceptacion", "Historial")


def _fail(message: str) -> NoReturn:
    raise ValueError(message)


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"Clave duplicada: {key}")
        result[key] = value
    return result


def _text(value: Any, *, required: bool = True) -> bool:
    return isinstance(value, str) and (bool(value.strip()) or not required)


def _identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"IMP-[0-9]{4,}", value) is not None
        and int(value[4:]) > 0
    )


def _date(value: Any) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)", value
    ):
        _fail("Fecha RFC3339 inválida")
    if value[-1] != "Z" and (int(value[-5:-3]) > 23 or int(value[-2:]) > 59):
        _fail("Offset RFC3339 inválido")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed


def _list(value: Any) -> bool:
    return isinstance(value, list)


def _reference(reference: Any, root: Path) -> None:
    if (
        not isinstance(reference, dict)
        or set(reference) != {"tipo", "destino", "etiqueta"}
        or not all(_text(v) for v in reference.values())
    ):
        _fail("Referencia inválida")
    target = reference["destino"]
    if reference["tipo"] == "https":
        try:
            url = urlsplit(target)
            valid = (
                url.scheme == "https"
                and bool(url.hostname)
                and not url.username
                and not url.password
                and not any(ord(c) < 33 for c in target)
                and "\\" not in target
            )
            _ = url.port
        except ValueError:
            valid = False
        if not valid:
            _fail("Referencia https inválida")
    elif reference["tipo"] == "archivo":
        windows = PureWindowsPath(target)
        parts = target.replace("\\", "/").split("/")
        if (
            windows.is_absolute()
            or windows.drive
            or any(p in {"..", "", "."} for p in parts)
            or any(ord(c) < 32 for c in target)
            or any(
                re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\..*)?", p)
                or ":" in p
                or p.endswith((".", " "))
                for p in parts
            )
        ):
            _fail("Ruta de referencia inválida")
        candidate = root.joinpath(*parts).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            _fail("Referencia fuera de raíz o inexistente")
    else:
        _fail("Tipo de referencia desconocido")


def project_identity(root: Path) -> str:
    """Obtiene la identidad del contrato de la raíz explícita, nunca del cwd."""
    text = (root / "coordinacion/PROYECTO.md").read_text(encoding="utf-8")
    matches = list(
        re.finditer(r"^- Identidad del registro: ([^\s.]+)\.$", text, re.MULTILINE)
    )
    if len(matches) != 1:
        _fail("Identidad del registro ausente o ambigua")
    roots = list(re.finditer(r"^- Raíz canónica: (.+)\.$", text, re.MULTILINE))
    if (
        len(roots) != 1
        or not Path(roots[0][1]).is_absolute()
        or Path(roots[0][1]).resolve() != root / "coordinacion"
    ):
        _fail("Raíz canónica ausente o distinta de la raíz efectiva")
    return matches[0][1]


def read_tasks(root: Path, ideas: set[int]) -> list[dict[str, Any]]:
    """Valida todos los tickets y las relaciones antes de devolver datos."""
    root = root.resolve()
    directory = root / "coordinacion/tareas"
    if not directory.exists():
        contract = root / "coordinacion/PROYECTO.md"
        if contract.exists() and re.search(
            r"(?m)^- Seguimiento local de ideas/tareas:",
            contract.read_text(encoding="utf-8"),
        ):
            project_identity(root)
            _fail("Fuente de tareas ausente con seguimiento local declarado")
        return []
    identity = project_identity(root)
    tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for folder in sorted(directory.iterdir()):
        if not folder.is_dir() or not _identifier(folder.name):
            _fail(f"Entrada de tareas inválida: {folder.name}")
        path = folder / "TAREA.md"
        if not path.resolve().is_relative_to(root) or not path.is_file():
            _fail("Ticket fuera de raíz o inexistente")
        source = path.read_text(encoding="utf-8")
        match = re.match(
            r"\A# ([^\n]+)\n\s*```json\n(.*?)\n```(?:\n|$)", source, re.DOTALL
        )
        if not match:
            _fail(f"Cabecera de ticket inválida: {folder.name}")
        data = json.loads(
            match[2],
            object_pairs_hook=_object,
            parse_constant=lambda value: _fail(f"Constante JSON inválida: {value}"),
        )
        if not isinstance(data, dict) or set(data) != FIELDS:
            _fail("Campos de metadata inválidos")
        if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
            _fail("Versión de ticket incompatible")
        if (
            not all(
                _text(data[k])
                for k in ("id", "projectId", "titulo", "origen", "responsable")
            )
            or data["id"] != folder.name
            or data["id"] in seen
            or data["projectId"] != identity
            or data["titulo"] != match[1]
        ):
            _fail("Identidad, ruta o título incoherente")
        seen.add(data["id"])
        if _date(data["actualizada"]) < _date(data["creada"]):
            _fail("Actualización anterior al alta")
        links = data["ideas"]
        if (
            not _list(links)
            or any(type(n) is not int or n <= 0 or n not in ideas for n in links)
            or len(links) != len(set(links))
        ):
            _fail("Ideas inválidas")
        if data["chat"] is not None and not _text(data["chat"]):
            _fail("Chat inválido")
        if data["fase"] not in PHASES or data["atencion"] not in ATTENTION:
            _fail("Fase o atención desconocida")
        if not all(
            _text(data[k], required=data["atencion"] != "normal")
            for k in ("motivo", "siguienteAccion")
        ):
            _fail("Motivo o siguiente acción inválidos")
        if data["fase"] in {"finalizada", "cancelada"} and data["atencion"] != "normal":
            _fail("Atención terminal inválida")
        auth = data["autorizacion"]
        if (
            not isinstance(auth, dict)
            or set(auth) != {"estado", "alcance", "referencia"}
            or auth["estado"]
            not in ("pendiente", "autorizada", "cancelacion_autorizada")
            or not all(
                _text(auth[k], required=auth["estado"] != "pendiente")
                for k in ("alcance", "referencia")
            )
        ):
            _fail("Autorización inválida")
        if (
            data["fase"] == "cancelada"
            and auth["estado"] != "cancelacion_autorizada"
            or data["fase"] not in {"pendiente", "cancelada"}
            and auth["estado"] != "autorizada"
        ):
            _fail("Fase sin autorización aplicable")
        dependencies = data["dependencias"]
        if (
            not _list(dependencies)
            or any(not _identifier(n) for n in dependencies)
            or len(dependencies) != len(set(dependencies))
            or data["id"] in dependencies
        ):
            _fail("Dependencias inválidas")
        if not _list(data["referencias"]):
            _fail("Referencias inválidas")
        for reference in data["referencias"]:
            _reference(reference, root)
        # Los encabezados dentro de bloques de código son contenido, no secciones.
        body = source[match.end() :]
        tokens = mistune.create_markdown(renderer="ast")(body)
        if not isinstance(tokens, list):
            _fail("No se pudo analizar el cuerpo Markdown")

        def plain(token: dict[str, Any]) -> str:
            return str(token.get("raw", "")) + "".join(
                plain(child) for child in token.get("children", [])
            )

        sections: dict[str, str] = {}
        headings: list[str] = []
        current = ""
        for token in tokens:
            if token["type"] == "heading" and token["attrs"]["level"] == 2:
                current = plain(token)
                headings.append(current)
                sections[current] = ""
            elif current:
                sections[current] += plain(token)
        if (
            any(headings.count(name) != 1 for name in SECTIONS)
            or not sections.get("Resultado", "").strip()
            or not sections.get("Alcance", "").strip()
            or not sections.get("Aceptacion", "").strip()
        ):
            _fail("Secciones del ticket incompletas")
        if (
            data["fase"] != "pendiente"
            and "Pendiente de concretar" in sections["Aceptacion"]
        ):
            _fail("Aceptación sin concretar")
        tasks.append({**data, "body": body})
    by_id = {t["id"]: t for t in tasks}
    visited: set[str] = set()
    active: set[str] = set()

    for identifier in by_id:
        stack = [(identifier, False)]
        while stack:
            identifier, exiting = stack.pop()
            if exiting:
                active.remove(identifier)
                visited.add(identifier)
                continue
            if identifier not in by_id or identifier in active:
                _fail("Dependencia ausente o ciclo")
            if identifier in visited:
                continue
            active.add(identifier)
            stack.append((identifier, True))
            stack.extend(
                (dependency, False) for dependency in by_id[identifier]["dependencias"]
            )
    return tasks
