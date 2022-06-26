from time import sleep
from smbus import SMBus
import requests
from datetime import datetime
import board
import adafruit_dht
import adafruit_ccs811
import busio

BOX_ID = 1

bus = SMBus(1)
address = 0x48
soil_address = 0x40

i2c = busio.I2C(board.SCL, board.SDA)
ccs = adafruit_ccs811.CCS811(i2c)

dhtDevice = adafruit_dht.DHT11(board.D18, use_pulseio=False) 

def soil_moisture(): 
    try :
        bus.write_byte(address, soil_address)
        data = bus.read_byte(address)
        data = (((data-22)/(255))*100)
        return round(data,2)
    except Exception as e:
        print("soil error")
        print(e)
        return 0
    
            
def co2_sensor():
    try:
        if ccs.data_ready:
            return ccs.eco2, ccs.tvoc
    except Exception as e :
        print("co2 error")
        print(e)
        return 0, 0


def temperature():
    for i in range(3):
        try:
            temp = dhtDevice.temperature
            humidity = dhtDevice.humidity
            return temp, humidity
        except Exception as e:
            print("dht error")
            print(e)
            continue
        
if __name__ == "__main__":
    ds = {}
    api_url = "http://my-biosphere.herokuapp.com/metrics/?format=api"

    try :
        soil = soil_moisture()
        d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        air = co2_sensor()
        temp = temperature()
        ds = {"box_id" : str(BOX_ID),
              "date" : str(d),
              "soil_humidity" : str(soil), 
              "fine_particle" : str(air[1]),
              "co2" : str(air[0]),
              "temperature" : str(temp[0]),
              "humidity" : str(temp[1])
              }
        r = requests.post(url = api_url, data = ds)
        print(r)
    except RuntimeError as error:
        print(str(datetime.now()))
        print(error)

