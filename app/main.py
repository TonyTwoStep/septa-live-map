import pandas as pd
import requests
import json
import re
import gmplot
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():

    df = get_recent_septa_data()

    label_list = generate_labels(df.Direction.tolist(),
                                 df.destination.tolist(),
                                 df.route.tolist(),
                                 df.late.tolist())

    map_html = draw_map(df, label_list)
    map_javascript = extract_js_from_html(map_html)

    return render_template('map-template.html', map_js=map_javascript)


def draw_map(df, label_list):
    # Add apikey parameter here if you have one
    gmap = gmplot.GoogleMapPlotter(39.954851, -75.181203, 15)
    gmap.scatter(df.lat.tolist(), df.lng.tolist(),
                 color='#ff0000',
                 s=15,
                 label=df.route.tolist(),
                 title=label_list,
                 precision=25,
                 alpha='1.0',
                 marker=True)

    return gmap.get()


def generate_labels(direction_list, destiation_list, route_list, late_list):
    late_list = ''.join(str(e) for e in late_list)
    directional_dests = [i + " towards " + j for i, j in zip(direction_list, destiation_list)]
    label_list = ["Route " + i + "\\n" + j for i, j in zip(route_list, directional_dests)]
    label_list = [i + "\\n" + "Running " + j + " minute(s) late" for i, j in zip(label_list, late_list)]
    return label_list


def get_recent_septa_data():
    url = "http://www3.septa.org/hackathon/TransitViewAll/"
    json_object = json.loads(requests.get(url).text)['routes'][0]
    df = pd.DataFrame()

    septa_route_numbers = []

    # Parse current json data into a dataframe
    for route, vehicles_in_route in json_object.items():
        for vehicle in vehicles_in_route:
            # add a new key value pair to the dic for the route
            vehicle['route'] = route

            # add a row in the dataframe for all of these vehicles
            df = df.append(vehicle, ignore_index=True)

    # Convert fields into proper data type
    df['lat'] = df['lat'].astype(float)
    df['lng'] = df['lng'].astype(float)
    df['VehicleID'] = df['VehicleID'].astype(int)
    df['BlockID'] = df['BlockID'].astype(int)
    df['trip'] = df['trip'].astype(int)
    df['Offset_sec'] = df['Offset_sec'].astype(int)
    df['label'] = df['label'].astype(int)

    return df


def extract_js_from_html(gmap_string):
    result = re.search('</title>\n((.|\n)*)</head>', gmap_string)
    result = result.group(1).replace('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAiCAYAAACwaJKDAAAABmJLR0QA/w'
                        'D/AP+gvaeTAAACBklEQVRIia3VzUtUURgH4GdG/AiyZZShtWgXUbSIFtGqRYtqWRLhXyBYf0K6MaJQ2g'
                        'RtayHtijYpleHKSCgIcRHoIiOSKEzLKea0OOeqTfPlzPzg5Qwz9zz3nXPvPTeneo7gNA4gjyI+Ygbva8'
                        'z9L2cxi9BHOE+4msY+gliz6biayWE0R7GfMEcoEkJJzRH6CbnY+WiaVxEc6yY8KQOVq8eE7tj1WCV4qI'
                        'swUyeY1QyhK8JDpWAP1m7vEMzqTkTXkrOZkYOEQoNogXAowiPE2wQuDqC9nktZJu0YSE72XRs2phrsMq'
                        'up2OkG2vLpRB19DXaZJc3vQHv294Um0e3z8yigsNQkmuYXUMie5/npJtE0fz55YLiXsNHELdUbV2B4+4'
                        'n2Y/Vmg+itCK4m558MdhBe7hCcJnRGdLDS0ox3E17XCb4h7IngeLX1zuFhD2G5BriytY4Tqmx9WXbh3T'
                        'nl99KsLkdwAbtrgVmO4/eDCuCkzd3/TL1glru9hF8lYJFwMoKPdgrCXqzfL0GfR7CIo42gcO9YCXopol'
                        'ONgnAC4W0Cv9l8dVxpBoWFGwmdiOC6Glc8X+3HlKeT6cOzOLzAjyaaBBc602ZzOHZ6vVkQ9kl7Qi6ip1'
                        'qBwpdrEfwjPnFVU8+awuKrOC7hZ6vQlQ9baM3Ui379HsfVVqKf07jcSvRTGhfrOfgvIP3ECS77BDoAAA'
                        'AASUVORK5CYII=', '/static/bus-small.png').replace(".maps.Point(10, 11)", ".maps.Point(12, -8)")
    return result


if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True, port=80)