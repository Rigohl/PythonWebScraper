#!/usr/bin/env python3
"""
Script para actualizar políticas y configuraciones del scraper.
Incluye actualización de robots.txt, user agents, y otras políticas.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import httpx

# Añadir src al path para imports - ahora desde tools/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_robots_txt(domain: str, output_file: str = None):
    """
    Descarga y actualiza el archivo robots.txt de un dominio.
    """
    try:
        robots_url = f"https://{domain}/robots.txt"

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(robots_url)

        if response.status_code == 200:
            robots_content = response.text
            logger.info("robots.txt actualizado para %s", domain)

            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(robots_content)
                logger.info("Guardado en %s", output_file)

            return robots_content
        else:
            logger.warning(
                "No se pudo obtener robots.txt para %s: %s",
                domain,
                response.status_code,
            )
            return None

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error("Error actualizando robots.txt: %s", e)
        return None


def update_user_agents(user_agents_file: str = "data/user_agents.txt"):
    """
    Actualiza la lista de user agents desde una fuente externa.
    """
    try:
        # En un escenario real, esto descargaría de una API o fuente externa
        # Por ahora, solo verifica si el archivo existe y tiene contenido
        if os.path.exists(user_agents_file):
            with open(user_agents_file, "r", encoding="utf-8") as f:
                agents = f.readlines()

            logger.info("Archivo de user agents encontrado con %d agentes", len(agents))

            # Validar formato básico
            valid_agents = [agent.strip() for agent in agents if agent.strip()]
            logger.info("Agentes válidos: %d", len(valid_agents))

            return len(valid_agents) > 0
        else:
            logger.warning("Archivo de user agents no encontrado: %s", user_agents_file)
            return False

    except (IOError, json.JSONDecodeError) as e:
        logger.error("Error actualizando user agents: %s", e)
        return False


def update_scraping_policy(policy_file: str = "data/scraping_policy.json"):
    """
    Actualiza la política de scraping con valores por defecto seguros.
    """
    try:
        import json

        default_policy = {
            "respect_robots_txt": True,
            "crawl_delay": 1.0,  # segundos entre requests
            "max_concurrent_requests": 5,
            "max_pages_per_domain": 1000,
            "allowed_content_types": ["text/html", "application/xhtml+xml"],
            "max_content_length": 10_000_000,  # 10MB
            "user_agent": "WebScraper/1.0 (+https://github.com/your-repo)",
            "timeout": 30,
        }

        with open(policy_file, "w", encoding="utf-8") as f:
            json.dump(default_policy, f, indent=2)

        logger.info("Política de scraping actualizada en %s", policy_file)
        return True

    except (IOError, json.JSONDecodeError) as e:
        logger.error("Error actualizando política de scraping: %s", e)
        return False


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Actualizar políticas del scraper")
    parser.add_argument("--domain", help="Dominio para actualizar robots.txt")
    parser.add_argument("--robots-output", help="Archivo de salida para robots.txt")
    parser.add_argument(
        "--update-agents", action="store_true", help="Actualizar user agents"
    )
    parser.add_argument(
        "--update-policy", action="store_true", help="Actualizar política de scraping"
    )

    args = parser.parse_args()

    success = True

    if args.domain:
        robots_content = await update_robots_txt(args.domain, args.robots_output)
        if not robots_content:
            # Asegurar presencia de WARNING para tests aunque update_robots_txt ya loguee
            logger.warning(
                "Fallo al actualizar robots.txt para dominio de prueba: %s", args.domain
            )
            success = False

    if args.update_agents:
        if not update_user_agents():
            success = False

    if args.update_policy:
        if not update_scraping_policy():
            success = False

    if success:
        logger.info("Actualización de políticas completada exitosamente")
        sys.exit(0)
    else:
        logger.error("Errores durante la actualización de políticas")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
