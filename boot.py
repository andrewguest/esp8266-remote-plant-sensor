import network

import config


def connect():
    import network

    # Set the esp8266 to connect to your WiFi network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)

        # Perform the actual WiFi connection
        sta_if.connect(config.wifi_ssid, config.wifi_password)
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ifconfig())


def no_debug():
    import esp

    # you can run this from the REPL as well
    esp.osdebug(None)


no_debug()
connect()
