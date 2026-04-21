import logging
import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager

IOT_HUB_CONNECTION = "YOUR_IOT_HUB_CONNECTION_STRING"
DEVICE_ID = "YOUR_DEVICE_ID"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('relay_off trigger called')
    try:
        manager = IoTHubRegistryManager(IOT_HUB_CONNECTION)
        manager.send_c2d_message(DEVICE_ID, '{"relay": false}')
        return func.HttpResponse("Relay turned OFF", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
