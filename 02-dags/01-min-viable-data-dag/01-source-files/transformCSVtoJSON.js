function transformCSVtoJSON(line) {
var values = line.split(',');

var obj = new Object();
obj.location = values[0];
obj.average_temperature = values[1];
obj.month = values[2];
obj.inches_of_rain = values[3];
obj.is_current = values[4];
obj.latest_measurement = values[5];

var jsonString = JSON.stringify(obj);

return jsonString;
}
