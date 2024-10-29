#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from flask import Flask, Response, request
from digitemp.master import UART_Adapter
from digitemp.device import DS18B20

app = Flask(__name__)

parser = argparse.ArgumentParser(description='Web server that publishes temperature from a DS18B20 1-wire temperature sensor')

parser.add_argument('--bus',
                    type=str,
                    help="hardware bus to read sensors",
                    default='/dev/ttyUSB0')

parser.add_argument('--port',
                    type=int,
                    help = "listen port for this server",
                    default='9500')

def start_server(port):
    app.run(host='0.0.0.0', port=port, debug=False)


def main():
    args = parser.parse_args()

    bus = UART_Adapter(args.bus)
    sensor = DS18B20(bus)
    sensor.set_resolution(DS18B20.RES_12_BIT)
    sensor.info()
    app.config['sensor'] = sensor
    
    print("starting server at port: %d" % args.port)
    start_server(args.port)


def get_ds18b20_temperature_reading():
    # assumes a single sensor on the bus
    sensor = app.config['sensor']
    return sensor.get_temperature()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/metrics")
def metrics():
    response = '\n'.join(['# HELP {metric} 1-wire temperature reading (celcius)',
                          '# TYPE {metric} gauge',
                          '{metric} {temperature}'])
    return Response(response.format(metric='ds18b20_temperature_celcius',
                                    temperature=get_ds18b20_temperature_reading()),
                                    mimetype='text/plain')

if __name__ == '__main__':
    main()
