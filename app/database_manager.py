"""
Database Manager - Solución definitiva para problemas de concurrencia
"""
import threading
import time
import sqlite3
from contextlib import contextmanager
from flask import current_app
from sqlalchemy.exc import OperationalError
import os

class DatabaseManager:
    """Manager centralizado para operaciones de base de datos thread-safe."""
    
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant lock
        self._connection_cache = {}
        
    @contextmanager
    def get_connection(self):
        """Obtener conexión thread-safe a la base de datos."""
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id not in self._connection_cache:
                # Crear nueva conexión para este thread
                db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                
                conn = sqlite3.connect(
                    db_path,
                    timeout=60.0,  # 60 segundos de timeout
                    check_same_thread=False,
                    isolation_level=None  # Autocommit mode
                )
                
                # Configurar pragmas optimizados
                cursor = conn.cursor()
                cursor.execute("PRAGMA busy_timeout=60000")  # 60 segundos
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=2000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA journal_mode=DELETE")  # Más compatible
                cursor.close()
                
                self._connection_cache[thread_id] = conn
            
            yield self._connection_cache[thread_id]
    
    def execute_with_retry(self, operation, max_retries=10):
        """Ejecutar operación con retry agresivo."""
        for attempt in range(max_retries):
            try:
                with self._lock:  # Global lock para todas las operaciones
                    return operation()
            except (OperationalError, sqlite3.OperationalError) as e:
                error_msg = str(e).lower()
                if "database is locked" in error_msg or "locked" in error_msg:
                    if attempt < max_retries - 1:
                        # Backoff agresivo
                        delay = 0.1 * (2 ** attempt) + (attempt * 0.05)
                        print(f"🔒 Database locked, intento {attempt + 1}/{max_retries}, esperando {delay:.2f}s...")
                        time.sleep(delay)
                        continue
                raise e
        
        raise Exception(f"❌ Database locked después de {max_retries} intentos")
    
    def cleanup_connections(self):
        """Limpiar conexiones del cache."""
        with self._lock:
            for conn in self._connection_cache.values():
                try:
                    conn.close()
                except:
                    pass
            self._connection_cache.clear()

# Instancia global del manager
db_manager = DatabaseManager()
