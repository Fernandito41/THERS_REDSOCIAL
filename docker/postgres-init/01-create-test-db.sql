-- Ejecutado una sola vez por la imagen oficial de postgres (docker-entrypoint-initdb.d)
-- cuando el volumen de datos está vacío. Crea una base separada para los tests
-- de backend (backend/tests/), para no correrlos contra thers_dev.
CREATE DATABASE thers_test OWNER thers;
