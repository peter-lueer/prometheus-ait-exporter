import os
import waitress
import flask
import socket

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    ip = flask.request.args.get('ip')
    port = flask.request.args.get('port')
    #record = flask.request.args.get('record')
    #ipv4 = flask.request.args.get('ipv4')
    #ipv6 = flask.request.args.get('ipv6')

    if not ip:
        return flask.jsonify({'status': 'error', 'message': 'Missing IP URL parameter.'}), 400
    if not port:
        return flask.jsonify({'status': 'error', 'message': 'Missing Port URL parameter.'}), 400
    #if not record:
    #    return flask.jsonify({'status': 'error', 'message': 'Missing record URL parameter.'}), 400
    #if not ipv4 and not ipv6:
    #    return flask.jsonify({'status': 'error', 'message': 'Missing ipv4 or ipv6 URL parameter.'}), 400

    print(f"Hello World")

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ip, port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                #while True:
                #    data = conn.recv(1024)
                #    if not data:
                #        break
                #    conn.sendall(data)

    except:
        return flask.jsonify({'status': 'error', 'message': 'Error.'}), 400



    
    return flask.jsonify({'status': 'success', 'message': 'Update successful.'}), 200


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    waitress.serve(app, host='0.0.0.0', port=80)

