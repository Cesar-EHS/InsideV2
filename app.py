from app import create_app

app = create_app()

if __name__ == '__main__':
    # --- Pega el bloque para imprimir las rutas aquí ---
    with app.app_context():
        print("--- RUTAS REGISTRADAS EN LA APLICACIÓN ---")
        for rule in app.url_map.iter_rules():
            # Imprime el endpoint, los métodos permitidos y la URL
            print(f"Endpoint: {rule.endpoint}, Methods: {','.join(rule.methods if rule.methods else [])}, URL: {rule.rule}")
        print("-------------------------------------------")
    # --- Fin del bloque ---
    app.run(host='0.0.0.0', port=8080, debug=True)
