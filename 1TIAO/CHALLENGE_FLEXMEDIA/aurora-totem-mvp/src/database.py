"""
Database Manager for Aurora Totem MVP
Handles Oracle FIAP connection and operations
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from .config import DATABASE_CONFIG, LOGGING_CONFIG

# Setup logging first
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

# Initialize Oracle Client libraries for macOS
def init_oracle_client():
    """Initialize Oracle client libraries with proper path for macOS"""
    try:
        # Check if Oracle libraries are available
        oracle_lib_paths = [
            "/opt/homebrew/lib",  # ARM64 Homebrew path
            "/usr/local/lib",     # Intel Homebrew path
            "/opt/oracle/instantclient_21_1",  # Standard Oracle path
        ]
        
        oracle_lib_path = None
        for path in oracle_lib_paths:
            if os.path.exists(os.path.join(path, "libclntsh.dylib")):
                oracle_lib_path = path
                break
        
        if oracle_lib_path:
            # Set environment variables for Oracle client
            os.environ['DYLD_LIBRARY_PATH'] = oracle_lib_path + ":" + os.environ.get('DYLD_LIBRARY_PATH', '')
            os.environ['ORACLE_HOME'] = oracle_lib_path
            print(f"🔧 Oracle client libraries found at: {oracle_lib_path}")
            return True
        else:
            print("⚠️ Oracle client libraries not found in standard locations")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing Oracle client: {e}")
        return False

# Try to initialize Oracle client
oracle_available = init_oracle_client()

# Import cx_Oracle only if Oracle is available, otherwise use fallback
try:
    import cx_Oracle
    ORACLE_AVAILABLE = True
    print("✅ cx_Oracle imported successfully")
except ImportError as e:
    print(f"⚠️ cx_Oracle import failed: {e}")
    print("🔄 Sistema funcionará sem Oracle (dados em memória)")
    ORACLE_AVAILABLE = False
    cx_Oracle = None

class DatabaseManager:
    """Manages Oracle FIAP database connections and operations"""
    
    # Shared fallback data across all instances when Oracle is unavailable
    _shared_fallback_data = []
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.fallback_data = DatabaseManager._shared_fallback_data  # Reference to shared storage
        
    def connect(self) -> bool:
        """
        Establish connection to Oracle FIAP database
        Returns True if successful, False otherwise
        """
        if not ORACLE_AVAILABLE:
            logger.warning("🔄 Oracle não disponível - usando armazenamento em memória")
            self.is_connected = True  # Allow system to continue
            return True
            
        try:
            logger.info("🔄 Tentando conectar ao Oracle FIAP...")
            
            # Create DSN (Data Source Name)
            dsn = cx_Oracle.makedsn(
                DATABASE_CONFIG['host'],
                DATABASE_CONFIG['port'], 
                sid=DATABASE_CONFIG['sid']
            )
            
            # Establish connection
            self.connection = cx_Oracle.connect(
                DATABASE_CONFIG['username'],
                DATABASE_CONFIG['password'],
                dsn,
                encoding="UTF-8"
            )
            
            self.is_connected = True
            logger.info("✅ Conectado ao Oracle FIAP com sucesso!")
            
            # Test connection with a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 'Connection Test' as status, SYSDATE as current_time FROM DUAL")
            result = cursor.fetchone()
            cursor.close()
            
            logger.info(f"📊 Teste de conexão: {result[0]} - {result[1]}")
            return True
            
        except cx_Oracle.Error as e:
            error, = e.args
            logger.error(f"❌ Erro na conexão Oracle: {error.message}")
            logger.error(f"   Código: {error.code}")
            self.is_connected = False
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro inesperado na conexão: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                self.is_connected = False
                logger.info("🔌 Conexão Oracle fechada")
            except Exception as e:
                logger.error(f"❌ Erro ao fechar conexão: {str(e)}")
    
    def test_connection(self) -> Dict[str, any]:
        """
        Test database connection and return status info
        """
        if not self.is_connected:
            if not self.connect():
                return {
                    "connected": False,
                    "error": "Falha na conexão inicial"
                }
        
        try:
            cursor = self.connection.cursor()
            
            # Get database info
            cursor.execute("""
                SELECT 
                    SYS_CONTEXT('USERENV', 'DB_NAME') as db_name,
                    SYS_CONTEXT('USERENV', 'SESSION_USER') as user_name,
                    SYS_CONTEXT('USERENV', 'SERVER_HOST') as host,
                    TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI:SS') as current_time
                FROM DUAL
            """)
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "connected": True,
                "database": result[0],
                "user": result[1],
                "host": result[2],
                "timestamp": result[3],
                "connection_string": f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['sid']}"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de conexão: {str(e)}")
            return {
                "connected": False,
                "error": str(e)
            }
    
    def create_tables(self) -> bool:
        """
        Create required tables for Aurora Totem
        Returns True if successful, False otherwise
        """
        if not self.is_connected:
            logger.error("❌ Não conectado ao banco de dados")
            return False
        
        tables_sql = {
            "sensor_data": """
                CREATE TABLE sensor_data (
                    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    device_id VARCHAR2(50) NOT NULL,
                    sensor_type VARCHAR2(20) NOT NULL,
                    sensor_value NUMBER(10,2) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata CLOB CHECK (metadata IS JSON),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "user_sessions": """
                CREATE TABLE user_sessions (
                    session_id RAW(16) DEFAULT sys_guid() PRIMARY KEY,
                    device_id VARCHAR2(50) NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    total_interactions NUMBER DEFAULT 0,
                    avg_emotion_score NUMBER(3,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "interactions_summary": """
                CREATE TABLE interactions_summary (
                    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    device_id VARCHAR2(50) NOT NULL,
                    date_summary DATE NOT NULL,
                    total_interactions NUMBER DEFAULT 0,
                    avg_touch_duration NUMBER(10,2),
                    avg_proximity NUMBER(10,2),
                    avg_emotion_score NUMBER(3,2),
                    ml_prediction_counts CLOB CHECK (ml_prediction_counts IS JSON),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        indexes_sql = [
            "CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp)",
            "CREATE INDEX idx_sensor_data_device ON sensor_data(device_id)",
            "CREATE INDEX idx_sensor_data_type ON sensor_data(sensor_type)",
            "CREATE INDEX idx_user_sessions_device ON user_sessions(device_id)",
            "CREATE INDEX idx_interactions_summary_date ON interactions_summary(date_summary)",
            "CREATE INDEX idx_interactions_summary_device ON interactions_summary(device_id)"
        ]
        
        try:
            cursor = self.connection.cursor()
            
            # Create tables
            for table_name, sql in tables_sql.items():
                try:
                    logger.info(f"🔄 Criando tabela {table_name}...")
                    cursor.execute(sql)
                    logger.info(f"✅ Tabela {table_name} criada com sucesso")
                except cx_Oracle.Error as e:
                    if "ORA-00955" in str(e):  # Table already exists
                        logger.info(f"ℹ️ Tabela {table_name} já existe")
                    else:
                        logger.error(f"❌ Erro ao criar tabela {table_name}: {str(e)}")
                        raise
            
            # Create indexes
            for idx_sql in indexes_sql:
                try:
                    cursor.execute(idx_sql)
                except cx_Oracle.Error as e:
                    if "ORA-00955" in str(e):  # Index already exists
                        continue
                    else:
                        logger.warning(f"⚠️ Erro ao criar índice: {str(e)}")
            
            self.connection.commit()
            cursor.close()
            
            logger.info("✅ Todas as tabelas e índices criados/verificados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na criação de tabelas: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def insert_sensor_data(self, device_id: str, sensor_type: str, 
                          sensor_value: float, metadata: Dict = None) -> bool:
        """
        Insert sensor data into database (Oracle or fallback memory)
        """
        if not self.is_connected:
            logger.error("❌ Não conectado ao banco de dados")
            return False
        
        # Fallback mode - store in memory
        if not ORACLE_AVAILABLE or not self.connection:
            try:
                record = {
                    'id': len(self.fallback_data) + 1,
                    'device_id': device_id,
                    'sensor_type': sensor_type,
                    'sensor_value': sensor_value,
                    'metadata': metadata,
                    'timestamp': datetime.now().isoformat()
                }
                self.fallback_data.append(record)
                logger.debug(f"💾 Dados em memória: {device_id} - {sensor_type}: {sensor_value}")
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao armazenar em memória: {str(e)}")
                return False
        
        # Oracle mode
        try:
            cursor = self.connection.cursor()
            
            sql = """
                INSERT INTO sensor_data (device_id, sensor_type, sensor_value, metadata)
                VALUES (:1, :2, :3, :4)
            """
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute(sql, (device_id, sensor_type, sensor_value, metadata_json))
            self.connection.commit()
            cursor.close()
            
            logger.debug(f"📊 Dados inseridos: {device_id} - {sensor_type}: {sensor_value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir dados: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_latest_data(self, limit: int = 10, device_id: str = None) -> List[Dict]:
        """
        Get latest sensor data (Oracle or fallback memory)
        """
        if not self.is_connected:
            logger.error("❌ Não conectado ao banco de dados")
            return []
        
        # Fallback mode - return from memory
        if not ORACLE_AVAILABLE or not self.connection:
            try:
                # Filter by device_id if specified
                data = self.fallback_data
                if device_id:
                    data = [record for record in data if record['device_id'] == device_id]
                
                # Sort by timestamp and limit
                sorted_data = sorted(data, key=lambda x: x['timestamp'], reverse=True)
                return sorted_data[:limit]
            except Exception as e:
                logger.error(f"❌ Erro ao consultar dados em memória: {str(e)}")
                return []
        
        # Oracle mode
        try:
            cursor = self.connection.cursor()
            
            if device_id:
                sql = """
                    SELECT device_id, sensor_type, sensor_value, timestamp, metadata
                    FROM sensor_data 
                    WHERE device_id = :1
                    ORDER BY timestamp DESC 
                    FETCH FIRST :2 ROWS ONLY
                """
                cursor.execute(sql, (device_id, limit))
            else:
                sql = """
                    SELECT device_id, sensor_type, sensor_value, timestamp, metadata
                    FROM sensor_data 
                    ORDER BY timestamp DESC 
                    FETCH FIRST :1 ROWS ONLY
                """
                cursor.execute(sql, (limit,))
            
            rows = cursor.fetchall()
            cursor.close()
            
            data = []
            for row in rows:
                # Handle CLOB metadata field
                metadata = {}
                if row[4]:
                    try:
                        metadata_str = row[4].read() if hasattr(row[4], 'read') else str(row[4])
                        metadata = json.loads(metadata_str) if metadata_str else {}
                    except:
                        metadata = {}
                
                data.append({
                    "device_id": row[0],
                    "sensor_type": row[1],
                    "sensor_value": float(row[2]),
                    "timestamp": row[3].isoformat(),
                    "metadata": metadata
                })
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar dados: {str(e)}")
            return []
    
    def get_data_by_timeframe(self, hours: int = 1, device_id: str = None) -> List[Dict]:
        """
        Get sensor data from last X hours
        """
        if not self.is_connected:
            logger.error("❌ Não conectado ao banco de dados")
            return []
        
        try:
            cursor = self.connection.cursor()
            
            if device_id:
                sql = """
                    SELECT device_id, sensor_type, sensor_value, timestamp, metadata
                    FROM sensor_data 
                    WHERE timestamp >= SYSTIMESTAMP - INTERVAL ':1' HOUR
                    AND device_id = :2
                    ORDER BY timestamp DESC
                """
                cursor.execute(sql, (hours, device_id))
            else:
                sql = """
                    SELECT device_id, sensor_type, sensor_value, timestamp, metadata
                    FROM sensor_data 
                    WHERE timestamp >= SYSTIMESTAMP - INTERVAL ':1' HOUR
                    ORDER BY timestamp DESC
                """
                cursor.execute(sql, (hours,))
            
            rows = cursor.fetchall()
            cursor.close()
            
            data = []
            for row in rows:
                # Handle CLOB metadata field
                metadata = {}
                if row[4]:
                    try:
                        metadata_str = row[4].read() if hasattr(row[4], 'read') else str(row[4])
                        metadata = json.loads(metadata_str) if metadata_str else {}
                    except:
                        metadata = {}
                
                data.append({
                    "device_id": row[0],
                    "sensor_type": row[1],
                    "sensor_value": float(row[2]),
                    "timestamp": row[3].isoformat(),
                    "metadata": metadata
                })
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar dados por tempo: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict:
        """
        Get database statistics (Oracle or fallback memory)
        """
        if not self.is_connected:
            return {"error": "Not connected"}
        
        # Fallback mode - stats from memory
        if not ORACLE_AVAILABLE or not self.connection:
            try:
                total_records = len(self.fallback_data)
                
                # Count by sensor type
                sensor_counts = {}
                device_counts = {}
                latest_timestamp = None
                
                for record in self.fallback_data:
                    # Sensor type counts
                    sensor_type = record['sensor_type']
                    sensor_counts[sensor_type] = sensor_counts.get(sensor_type, 0) + 1
                    
                    # Device counts
                    device_id = record['device_id']
                    device_counts[device_id] = device_counts.get(device_id, 0) + 1
                    
                    # Latest timestamp
                    timestamp = record['timestamp']
                    if not latest_timestamp or timestamp > latest_timestamp:
                        latest_timestamp = timestamp
                
                return {
                    "total_records": total_records,
                    "sensor_counts": sensor_counts,
                    "device_counts": device_counts,
                    "latest_timestamp": latest_timestamp,
                    "storage_mode": "memory"
                }
                
            except Exception as e:
                logger.error(f"❌ Erro ao obter estatísticas da memória: {str(e)}")
                return {"error": str(e)}
        
        # Oracle mode
        try:
            cursor = self.connection.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            total_records = cursor.fetchone()[0]
            
            # Records by sensor type
            cursor.execute("""
                SELECT sensor_type, COUNT(*) as count 
                FROM sensor_data 
                GROUP BY sensor_type 
                ORDER BY count DESC
            """)
            sensor_counts = dict(cursor.fetchall())
            
            # Records by device
            cursor.execute("""
                SELECT device_id, COUNT(*) as count 
                FROM sensor_data 
                GROUP BY device_id 
                ORDER BY count DESC
            """)
            device_counts = dict(cursor.fetchall())
            
            # Latest timestamp
            cursor.execute("SELECT MAX(timestamp) FROM sensor_data")
            latest_timestamp = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                "total_records": total_records,
                "sensor_counts": sensor_counts,
                "device_counts": device_counts,
                "latest_timestamp": latest_timestamp.isoformat() if latest_timestamp else None,
                "storage_mode": "oracle"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {"error": str(e)}
    
    def insert_user_session(self, session_id: str, device_id: str, 
                           user_age: Optional[int] = None, user_gender: Optional[str] = None,
                           interaction_duration: Optional[float] = None, 
                           emotions_detected: Optional[List[str]] = None,
                           engagement_score: Optional[float] = None,
                           metadata: Optional[Dict] = None) -> bool:
        """
        Insert user session data into user_sessions table
        """
        if not self.is_connected:
            logger.error("❌ Não conectado ao banco de dados")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Convert lists to JSON strings for storage
            emotions_json = json.dumps(emotions_detected) if emotions_detected else None
            metadata_json = json.dumps(metadata) if metadata else None
            
            sql = """
                INSERT INTO user_sessions 
                (session_id, device_id, user_age, user_gender, interaction_duration, 
                 emotions_detected, engagement_score, metadata, timestamp)
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, SYSTIMESTAMP)
            """
            
            cursor.execute(sql, (
                session_id,
                device_id, 
                user_age,
                user_gender,
                interaction_duration,
                emotions_json,
                engagement_score,
                metadata_json
            ))
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"✅ Sessão de usuário inserida: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir sessão de usuário: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False

def main():
    """
    Test database connection and operations
    """
    print("🌟 Aurora Totem - Database Manager")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # Test connection
    print("\n1️⃣ Testando conexão...")
    if db.connect():
        print("✅ Conexão estabelecida!")
        
        # Get connection info
        info = db.test_connection()
        if info['connected']:
            print(f"   📊 Banco: {info['database']}")
            print(f"   👤 Usuário: {info['user']}")
            print(f"   🖥️ Host: {info['host']}")
            print(f"   🕐 Timestamp: {info['timestamp']}")
    else:
        print("❌ Falha na conexão!")
        print("\n💡 Possíveis soluções:")
        print("   - Verifique VPN/rede FIAP")
        print("   - Confirme credenciais no config.py")
        print("   - Teste conexão manual via SQL Developer")
        return
    
    # Test table creation
    print(f"\n2️⃣ Criando/verificando tabelas...")
    if db.create_tables():
        print("✅ Tabelas criadas/verificadas com sucesso!")
    else:
        print("❌ Erro na criação de tabelas")
        print("\n💡 Use SQL Developer para criar manualmente:")
        print("   Consulte os scripts SQL no código database.py")
    
    # Test data insertion
    print(f"\n3️⃣ Testando inserção de dados...")
    test_success = db.insert_sensor_data(
        device_id="totem_test_001",
        sensor_type="test", 
        sensor_value=99.9,
        metadata={"test": True, "timestamp": datetime.now().isoformat()}
    )
    
    if test_success:
        print("✅ Inserção de teste bem-sucedida!")
        
        # Test data retrieval
        print(f"\n4️⃣ Testando consulta de dados...")
        latest_data = db.get_latest_data(limit=5)
        if latest_data:
            print(f"✅ Encontrados {len(latest_data)} registros:")
            for record in latest_data[:3]:  # Show first 3
                print(f"   📊 {record['device_id']} - {record['sensor_type']}: {record['sensor_value']}")
        
        # Get statistics
        print(f"\n5️⃣ Estatísticas do banco:")
        stats = db.get_database_stats()
        if 'error' not in stats:
            print(f"   📊 Total registros: {stats['total_records']}")
            print(f"   📈 Por sensor: {stats['sensor_counts']}")
            print(f"   📱 Por device: {stats['device_counts']}")
        
    else:
        print("❌ Falha na inserção de teste")
    
    # Close connection
    db.disconnect()
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    main()