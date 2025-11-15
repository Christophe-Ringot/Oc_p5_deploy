#!/usr/bin/env python3
"""Script de test rapide pour vérifier DATABASE_URL"""

from app.database import DATABASE_URL, engine

print(f"DATABASE_URL: {DATABASE_URL}")
print(f"Engine URL: {engine.url}")
print(f"Dialecte: {engine.dialect.name}")

if "sqlite" in str(engine.url).lower():
    print("✅ SQLite est utilisé")
elif "postgresql" in str(engine.url).lower():
    print("✅ PostgreSQL est utilisé")
else:
    print("❌ Base de données inconnue")
