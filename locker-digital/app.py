# PUNTO DE ENTRADA DE LA APP

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)