from app import app
import socket

def get_local_ip():
    """
    Trova l'indirizzo IP locale del computer sulla rete.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Non deve essere un indirizzo raggiungibile, serve solo per aprire un socket
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Fallback in caso di problemi
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    local_ip = get_local_ip()
    
    print("****************************************************")
    print(f" Avvio di PennyPilot in modalità sviluppo...")
    print(f" Accessibile da questo computer su: http://127.0.0.1:{port}")
    print(f" Accessibile da altri dispositivi sulla rete su: http://{local_ip}:{port}")
    print("****************************************************")
    
    app.run(host=host, port=port, debug=True)