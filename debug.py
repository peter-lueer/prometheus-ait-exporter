from io import BufferedReader
import os
import waitress
import flask
import socket

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    ip = flask.request.args.get('ip')
    port = int(flask.request.args.get('port'))
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
            s.connect((ip,port))
            toSend = [0,0,11,188]
            s.send(bytearray(toSend))
            toSend = [0,0,0,0]
            s.send(bytearray(toSend))
            
            recievedData = s.recv(4096)
            i=0
            id=0
            while True: 
                try:
                    testArray=recievedData[i+3]
                except Exception as e:
                    break

                result = 0
                result = ((recievedData[i+3]) |
                (recievedData[i + 2] << 8) |
                (recievedData[i + 1] << 16) |
                (recievedData[i] << 24))

                # setValue(id, result);
                i += 4
                id += 1


    except Exception as ex:
        return flask.jsonify({'status': 'error', 'message': 'Error.' + ex}), 400



    
    return flask.jsonify({'status': 'success', 'message': 'Update successful.'}), 200


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    waitress.serve(app, host='0.0.0.0', port=80)

