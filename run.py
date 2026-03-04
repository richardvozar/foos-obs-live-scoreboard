from app import create_app

app = create_app()

if __name__ == "__main__":
    # OBS-hez jobb a fixed host/port
    app.run(host="127.0.0.1", port=8765, debug=False)