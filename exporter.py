import argparse
import datetime
import json
import logging
import prometheus_client
import socket
import sys
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")


class Exporter(object):
    """
    Prometheus Exporter for Alpha Innotec 
    """
    def __init__(self, args):
        """
        initializes the exporter

        :param args: the argparse.Args
        """
        
        self.__metric_port = int(args.metric_port)
        self.__collect_interval_seconds = args.collect_interval_seconds
        self.__log_level = int(args.log_level)

        logging.info(
            "using config file '{}' and exposing metrics on port '{}'".format(args.config_file, self.__metric_port)
        )

        self.__init_client(args.config_file, args.ait_ip, args.ait_port)
        self.__init_metrics()
        try:
            prometheus_client.start_http_server(self.__metric_port)
        except Exception as e:
            logging.fatal(
                "starting the http server on port '{}' failed with: {}".format(self.__metric_port, str(e))
            )
            sys.exit(1)

    def __init_client(self, config_file, ait_ip, ait_port):

        try:
            self.ait_ip = ait_ip
            self.ait_port = int(ait_port)
            
            logging.info(
                "Initializing Method - no init needed yet"
            )
        except Exception as e:
            logging.fatal(
                "Initializing failed with: {}".format(str(e))
            )
            sys.exit(1)

    def __init_metrics(self):
        namespace = 'ait'

        self.version_info = prometheus_client.Gauge(
            name = 'version_info',
            documentation = 'Project version info',
            labelnames = ['project_version'],
            namespace = namespace
        )

        self.metrics = {}

        objectFile = open('objectlist.json')
        self.objectList = json.load(objectFile)

        for data in self.objectList:
            try:
                metrics_data=self.objectList[data]
                name = metrics_data["name"]
                documentation = metrics_data["name"]
                index = self.addPrefix(data)
                try:
                    dataType = metrics_data["type"]
                except:
                    dataType = ""

                if dataType == "TEMPERATURE":
                    self.metrics[index] = prometheus_client.Gauge(
                        name = name,
                        documentation = documentation,
                        namespace = namespace
                    )
                elif dataType == "IO":
                    self.metrics[index] = prometheus_client.Gauge(
                        name = name,
                        documentation = documentation,
                        namespace = namespace
                    )
                elif dataType == "SECONDS":
                    self.metrics[index] = prometheus_client.Gauge(
                        name = name,
                        documentation = documentation,
                        namespace = namespace
                    )
                elif dataType == "TIMESTAMP":
                    self.metrics[index] = prometheus_client.Gauge(
                        name = name,
                        documentation = documentation,
                        namespace = namespace
                    )
                elif dataType == "COUNTER":
                    self.metrics[index] = prometheus_client.Gauge(
                        name = name,
                        documentation = documentation,
                        namespace = namespace
                    )
                elif dataType == "IP":
                    #do not save IP Information
                    self.metrics[index] = prometheus_client.Info(
                        name = name,
                        documentation = documentation,
                        namespace = namespace
                    )
                    nothing="empty"

                elif dataType == "ENUM":
                    self.metrics[index] = prometheus_client.Enum(
                        name = name,
                        documentation = documentation,
                        namespace = namespace,
                        states = metrics_data['enum']
                    )
                
                else:
                    self.metrics[index] = prometheus_client.Gauge(
                        name = name,
                        documentation = documentation,
                        namespace = namespace
                    )

                #print(data + "- " + self.objectList[data]["name"] + ": ")
            except Exception as ex:
                #no Name found
                name=""

    def __collect_device_info_metrics(self):
        logging.info(
            "collect info metrics"
        )
        # general device info metric
        self.version_info.labels(
            project_version="0.1"
        ).set(1)

    def typeExists(self, listelement):
        try:
            dataType = listelement['type']
            return True
        except:
            return False
        #'type' in objectList[index]


    def isset(self, listelement):
        try:
            if listelement == {}:
                return False
            else:
                return True
        except:
            return False

    def int2ip(self, v):
        part1 = v & 255
        part2 = ((v >> 8) & 255)
        part3 = ((v >> 16) & 255)
        part4 = ((v >> 24) & 255)

        return str(part4) + "." + str(part3) + "." + str(part2) + "." + str(part1)

    def addPrefix(self, index):
        result = str(index)
        while len(result) < 3 :
            result = "0" + result
        return result

    def setMetricsValue(self, id, value):
        #logging.info("Set Value for {0}: {1}", id, value)
        try:
            state = value
            if (id>=0 and self.isset(self.objectList[str(id)]) and self.typeExists(self.objectList[str(id)])):
                index = self.addPrefix(id)
                dataType = self.objectList[str(id)]['type']
                if dataType == "TEMPERATURE" or dataType == "ANALOG":
                    state = int(value)/10
                elif dataType == "IO":
                    state = value > 0
                elif dataType == "IP":
                    state = self.int2ip(value)
                    self.metrics[index].info({ self.objectList[str(id)]['name'] : state})
                    return
                elif dataType == "ENUM":
                    state = self.objectList[str(id)]['enum'][value]
                    self.metrics[index].state(state)
                    return
                
                self.metrics[index].set(state)
            else:
                logging.info("Date not saved. ID:" + str(id) + " Value:" + str(value))
        except Exception as ex:
            logging.info("Date not saved. ID:" + str(id) + " Value:" + str(value))
            error="Set Value Error"


    def __collect_data_from_AIT(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ait_ip, self.ait_port))
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

                    self.setMetricsValue(id, result)
                    i += 4
                    id += 1

        except Exception as ex:
            logging.error('Fail while Reading from Socket')

    def collect(self):
        """
        collect discovers all devices and generates metrics
        """
        try:
            logging.info('Start collect method')

            #Collect Data from AIT Heating
            self.__collect_device_info_metrics()

            self.__collect_data_from_AIT()
        
        except Exception as e:
            logging.warning(
                "collecting data from ait failed with: {1}".format(str(e))
            )
        finally:
            logging.info('waiting {}s before next collection cycle'.format(self.__collect_interval_seconds))
            time.sleep(self.__collect_interval_seconds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Alpha-Innotec Prometheus Exporter',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--metric-port',
                        default=9100,
                        help='port to expose the metrics on')
    parser.add_argument('--config-file',
                        default='/etc/ait/config.ini',
                        help='path to the configuration file')
    parser.add_argument('--collect-interval-seconds',
                        default=30,
                        help='collection interval in seconds')
    parser.add_argument('--ait-ip',
                        default=None,
                        help='IP of ait device')
    parser.add_argument('--ait-port',
                        default=8888,
                        help='Port of ait device (default is 8888 or 8889)')
    parser.add_argument('--log-level',
                        default=30,
                        help='log level')

    # Start up the server to expose the metrics.
    e = Exporter(parser.parse_args())
    # Generate some requests.
    while True:
        e.collect()