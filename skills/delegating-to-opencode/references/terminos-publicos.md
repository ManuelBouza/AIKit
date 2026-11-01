# Términos públicos de acceso

`availability import --cwd <proyecto> --file <artefacto.json>` incorpora hechos
públicos validados al estado compartido. El artefacto debe contener
`public_terms` (o alias `public_facts`, `terms`, `facts`, `items`) con objetos que
incluyan `provider`, `model` y `source_url` HTTPS. No consulta red.

`free_candidate` sigue significando solo tarifa publicada cero. Los hechos públicos
pueden marcar `access_kind: conditional_access` para ofertas documentadas que no
acreditan cuota ni plan. No transfieren ofertas entre proveedores.