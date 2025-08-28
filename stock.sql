--!SQLITE3

PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS productos (
    cdb INTEGER PRIMARY KEY, --- Código de barras 
    nombre TEXT NOT NULL, --- Nombre del producto
    precio REAL NOT NULL, --- Precio del producto
    cantidad INTEGER DEFAULT 0,
    umbral INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cdb INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    precio_venta REAL,
    FOREIGN KEY (cdb) REFERENCES productos(cdb)
);

CREATE TABLE IF NOT EXISTS dinero (
    id INTEGER PRIMARY KEY CHECK (id = 1), --- Siempre será 1
    total REAL DEFAULT 0
);

INSERT INTO dinero (id, total) VALUES(1, 0);