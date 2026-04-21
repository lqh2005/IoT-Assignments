import logging
import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager

IOT_HUB_CONNECTION = "YOUR_IOT_HUB_CONNECTION_STRING"
DEVICE_ID = "YOUR_DEVICE_ID"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('relay_on trigger called')
    try:
        manager = IoTHubRegistryManager(IOT_HUB_CONNECTION)
        manager.send_c2d_message(DEVICE_ID, '{"relay": true}')
        return func.HttpResponse("Relay turned ON", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
