--!SQLITE3

PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS producto (
    cdb INTEGER PRIMARY KEY, --- Código de barras 
    nombre TEXT NOT NULL, --- Nombre del producto
    precio REAL NOT NULL, --- Precio del producto
    cantidad INTEGER DEFAULT 0, --- Cantidad en stock
    umbral INTEGER DEFAULT 0, --- Umbral de stock para alertas
    margen REAL DEFAULT 0.20 --- Margen de ganancia
);

CREATE TABLE IF NOT EXISTS venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS venta_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cdb INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_venta REAL,
    venta INTEGER,
    FOREIGN KEY (venta) REFERENCES venta(id),
    FOREIGN KEY (cdb) REFERENCES producto(cdb)
);

CREATE TABLE IF NOT EXISTS compra (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compra_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cdb INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_compra REAL,
    compra INTEGER,
    FOREIGN KEY (compra) REFERENCES compra(id),
    FOREIGN KEY (cdb) REFERENCES producto(cdb)
);

CREATE TABLE IF NOT EXISTS dinero (
    id INTEGER PRIMARY KEY CHECK (id = 1), --- Siempre será 1
    total REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS configuracion (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    fg TEXT,
    bg TEXT,
    font_name TEXT,
    font_size INTEGER
);

INSERT INTO dinero (id, total) VALUES(1, 0);

CREATE TABLE IF NOT EXISTS configuracion (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    fg TEXT,
    bg TEXT,
    passwd TEXT, -- ni idea de por que no inserta esta columna, pero bueno
    font_name TEXT,
    font_size INTEGER
);

ALTER TABLE configuracion ADD COLUMN passwd TEXT; -- atada con alambre

INSERT INTO configuracion (id, fg, bg, font_name, font_size, passwd) 
    VALUES (1, '#FFFFFF', '#000000', 'Arial', '12', '123456')