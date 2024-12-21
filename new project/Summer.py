import requests
import os

def get_user_location():
    try:
        # IP 위치 추적 서비스 API URL
        url = 'http://ipinfo.io/json'
        # API 요청 보내기
        response = requests.get(url)
        
        # 응답 데이터 파싱
        if response.status_code == 200:
            data = response.json()
            # 위치 정보 출력
            ## print(f"나의 위치: {data['city']}, {data['region']}, {data['country']} ({data['loc']})")
            return data
        else:
            print("위치 정보를 가져올 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

def get_weather_info(api_key, lat, lon):
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("날씨 정보를 가져올 수 없습니다.")
            return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def calculate_discomfort_index(temp, humidity):
    discomfort_index = 9/5 * temp - 0.55 * (1 - humidity / 100) * (9/5 * temp - 26) + 32
    return discomfort_index

def calculate_wind_chill(temp, wind_speed):
    wind_chill = 13.12 + 0.6215 * temp - 11.37 * (wind_speed ** 0.16) + 0.3965 * temp * (wind_speed ** 0.16)
    return wind_chill

def get_user_input():
    fan_power = float(input("선풍기의 소비 전력을 와트(W) 단위로 입력하세요: "))
    aircon_power = float(input("에어컨의 소비 전력을 와트(W) 단위로 입력하세요: "))
    desired_temperature = float(input("희망온도를 입력하세요: "))
    return fan_power, aircon_power, desired_temperature

def is_rainy_weather(weather_data):
    weather_conditions = [weather['main'] for weather in weather_data['weather']]
    return 'Rain' in weather_conditions

def calculate_electricity_cost(power, hours, rate_per_kwh):
    kwh = power / 1000
    cost = kwh * hours * rate_per_kwh
    return cost

def main():
    # 발급받은 OpenWeatherMap API 키 입력
    API_KEY = 'b20f717c7556089f8928babc4cecda7c'

    # 사용자의 위치 정보 받아오기
    location = get_user_location()
    if location:
        lat, lon = location['loc'].split(',')
        weather_data = get_weather_info(API_KEY, lat, lon)

        if weather_data:
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']

            discomfort_index = calculate_discomfort_index(temp, humidity)
            wind_chill = calculate_wind_chill(temp, wind_speed)

            print(f"현재 날씨 정보:")
            print(f"온도: {temp}°C")
            print(f"습도: {humidity}%")
            print(f"불쾌지수: {discomfort_index}°F")
            print(f"체감기온: {wind_chill}°C")

            fan_power, aircon_power, desired_temperature = get_user_input()
            is_rainy = is_rainy_weather(weather_data)

            # house_area = 30  # 30평을 기준으로 계산 (집의 면적)

            electricity_rate_low_1 = 112  # 주택용 전력(저압) 300kwh 이하 사용 1kWh 당 전기 요금
            electricity_rate_low_3 = 299.3 # 주택용 전력(저압) 450kwh 초과 사용 1kWh 당 전기 요금
            electricity_rate_low_super = 736.2 # 주택용 전력(저압) 1000kwh 초과 사용 1kWh 당 전기 요금
            electricity_rate_high_1 = 97 # 주택용 전력(고압) 300kwh 이하 사용 1kWh 당 전기 요금
            electricity_rate_high_3 = 234.3 # 주택용 전력(고압) 450kwh 초과 사용 1kWh 당 전기 요금
            electricity_rate_high_super = 593.3 # 주택용 전력(고압) 1000kwh 초과 사용 1kWh 당 전기 요금

            # 선풍기로 낮출 수 있는 최재치 설정
            fan_chill_temp_limit = 2 # 선풍기로 체감기온 낮출 수 있는 최대지를 2도로 설정
            fan_discomfort_index_limit = 3 # 선풍기로 불쾌지수 낮출 수 있는 최대치를 3으로 설정

            # 선풍기를 사용하여 1시간 후 체감기온과 불쾌지수를 계산
            fan_chill_temp = (wind_chill - fan_chill_temp_limit) # 선풍기로 체감기온 1도를 낮추는데 걸리는 시간 약 30분으로 상정
            fan_discomfort_index = (discomfort_index - fan_discomfort_index_limit) # 선풍기로 불쾌지수 1 낮추는데 걸리는 시간 약 20분으로 상정

            # 창문을 열고 선풍기로 낮출 수 있는 최재치 설정
            fan_window_chill_temp_limit = 4 # 창문을 열고 선풍기로 체감기온 낮출 수 있는 최대지를 4도로 설정
            fan_window_discomfort_index_limit = 6 # 창문을 열고 선풍기로 불쾌지수 낮출 수 있는 최대치를 6으로 설정

            # 선풍기를 사용하고 창문을 개방했을 시 1시간 후 체감기온과 불쾌지수를 계산
            fan_window_chill_temp = (wind_chill - fan_window_chill_temp_limit) # 창문을 열고 선풍기로 체감기온 1도를 낮추는데 걸리는 시간의 1/2로 상정
            fan_window_discomfort_index = (discomfort_index - fan_window_discomfort_index_limit) # 창문을 열고 선풍기로 불쾌지수 1 낮추는데 걸리는 시간의 1/2로 상정

            # 에어컨을 사용하여 1시간 후 체감기온과 불쾌지수를 계산
            aircon_chill_temp = (wind_chill - 6) # 에어컨 사용 체감기온 1도를 낮추는데 걸리는 시간 약 10분으로 상정
            aircon_discomfort_index = (discomfort_index - 6) # 에어컨 사용 불쾌지수 1 낮추는데 걸리는 시간 약 10분으로 상정

            # 예상 전기세 계산
            fan_electricity_cost_low_1 = calculate_electricity_cost(fan_power, 1, electricity_rate_low_1)
            fan_electricity_cost_low_3 = calculate_electricity_cost(fan_power, 1, electricity_rate_low_3)
            fan_electricity_cost_low_super = calculate_electricity_cost(fan_power, 1, electricity_rate_low_super)
            fan_electricity_cost_high_1 = calculate_electricity_cost(fan_power, 1, electricity_rate_high_1)
            fan_electricity_cost_high_3 = calculate_electricity_cost(fan_power, 1, electricity_rate_high_3)
            fan_electricity_cost_high_super = calculate_electricity_cost(fan_power, 1, electricity_rate_high_super)

            aircon_electricity_cost_low_1 = calculate_electricity_cost(aircon_power, 1, electricity_rate_low_1)
            aircon_electricity_cost_low_3 = calculate_electricity_cost(aircon_power, 1, electricity_rate_low_3)
            aircon_electricity_cost_low_super = calculate_electricity_cost(aircon_power, 1, electricity_rate_low_super)
            aircon_electricity_cost_high_1 = calculate_electricity_cost(aircon_power, 1, electricity_rate_high_1)
            aircon_electricity_cost_high_3 = calculate_electricity_cost(aircon_power, 1, electricity_rate_high_3)
            aircon_electricity_cost_high_super = calculate_electricity_cost(aircon_power, 1, electricity_rate_high_super)

            if not is_rainy: # 비가 오지 않는 경우

                # 선풍기를 사용하여 체감기온이 희망온도 이하이고 불쾌지수가 68 이하인지 판단
                if temp - desired_temperature <= wind_chill - fan_window_chill_temp:
                    print("선풍기 사용을 권장합니다.")
                    print(f"저압으로 전력을 공급받는 고객 선풍기 사용 시 예상 전기세: {fan_electricity_cost_low_1}원 ~ {fan_electricity_cost_low_3}원으로 예상되며 최대{fan_electricity_cost_low_super}원")
                    print(f"고압으로 전력을 공급받는 고객 선풍기 사용 시 예상 전기세: {fan_electricity_cost_high_1}원 ~ {fan_electricity_cost_high_3}원으로 예상되며 최대{fan_electricity_cost_high_super}원")
                    print(f"선풍기 사용 시 예상 체감기온{fan_window_chill_temp}, 예상 불쾌지수{fan_window_discomfort_index}")
                else:
                    print("에어컨 사용을 권장합니다.")
                    print(f"저압으로 전력을 공급받는 고객 에어컨 사용 시 예상 전기세: {aircon_electricity_cost_low_1}원 ~ {aircon_electricity_cost_low_3}원으로 예상되며 최대{aircon_electricity_cost_low_super}원")
                    print(f"고압으로 전력을 공급받는 고객 에어컨 사용 시 예상 전기세: {aircon_electricity_cost_high_1}원 ~ {aircon_electricity_cost_high_3}원으로 예상되며 최대{aircon_electricity_cost_high_super}원")
                    print(f"에어컨 사용 시 예상 체감기온{aircon_chill_temp}, 예상 불쾌지수{aircon_discomfort_index}")
            else:  # 비가 오는 경우

                # 선풍기를 사용하여 체감기온이 희망온도 이하이고 불쾌지수가 68 이하인지 판단
                if  temp - desired_temperature <= wind_chill - fan_chill_temp:
                    print("선풍기 사용을 권장합니다.")
                    print(f"저압으로 전력을 공급받는 고객 선풍기 사용 시 예상 전기세: {fan_electricity_cost_low_1}원 ~ {fan_electricity_cost_low_3}원으로 예상되며 최대{fan_electricity_cost_low_super}원")
                    print(f"고압으로 전력을 공급받는 고객 선풍기 사용 시 예상 전기세: {fan_electricity_cost_high_1}원 ~ {fan_electricity_cost_high_3}원으로 예상되며 최대{fan_electricity_cost_high_super}원")
                    print(f"선풍기 사용 시 예상 체감기온{fan_chill_temp}, 예상 불쾌지수{fan_discomfort_index}")

                else:
                    print("에어컨 사용을 권장합니다.")
                    print(f"저압으로 전력을 공급받는 고객 에어컨 사용 시 예상 전기세: {aircon_electricity_cost_low_1}원 ~ {aircon_electricity_cost_low_3}원으로 예상되며 최대{aircon_electricity_cost_low_super}원")
                    print(f"고압으로 전력을 공급받는 고객 에어컨 사용 시 예상 전기세: {aircon_electricity_cost_high_1}원 ~ {aircon_electricity_cost_high_3}원으로 예상되며 최대{aircon_electricity_cost_high_super}원")
                    print(f"에어컨 사용 시 예상 체감기온{aircon_chill_temp}, 예상 불쾌지수{aircon_discomfort_index}")

if __name__ == "__main__":
    main()
    print("30평 기준으로 1시간동안 가동했을 경우를 가정하였습니다.")
    os.system('pause')

