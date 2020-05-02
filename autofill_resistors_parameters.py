class AutofillDescription:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.partkeepr = Partkeepr(config)
        self.partkeepr.get_components()  # this will create resistors.json and capacitors.json
        with open("resistors.json") as file:
            self.resistors = json.load(file)
        with open("capacitors.json") as file:
            self.capacitors = json.load(file)

    def autofill_resistor_parameters(self, part, resistor):
        if not part.has_parameter('Resistance') and resistor.resistance is not None:
            part.add_parameter('Resistance', resistor.resistance)
        if not part.has_parameter('Tolerance') and resistor.tolerance is not None:
            part.add_parameter('Tolerance', resistor.tolerance)
        if not part.has_parameter('Working Temperature') and resistor.working_temperature_range is not None:
            part.add_parameter('Working Temperature', resistor.working_temperature_range)
        if not part.has_parameter("Voltage") and resistor.max_working_voltage is not None:
            part.add_parameter("Voltage", resistor.max_working_voltage, numeric_value_field='maxVoltage')
        if not part.has_parameter('Power') and resistor.power is not None:
            part.add_parameter('Power', resistor.power)
        return part

    def autofill_resistor(self, partkeepr_id, resistor):
        part = self.partkeepr.get_part(partkeepr_id)
        part = self.autofill_resistor_parameters(part, resistor)
        if resistor.note is not None:
            part.set_comment(resistor.note)




    def add_parameters(self):
        for resistor in self.resistors:
            if resistor['partkeepr_id'] in skip_autofill.autofill_description:
                print("Skipping description update of part: ", resistor['partkeepr_id'], " found in skip list.")
                continue
            if len(resistor['manufacturers']):
                manufacturer_part_number = resistor["manufacturers"][0]['partNumber']
                resistor_from_partname = resistors_partname_decoder.resolve(manufacturer_part_number)
                if resistor_from_partname is not None:
                    if 'Working Temperature' not in resistor['parameters'] and \
                            resistor_from_partname.working_temperature_range is not None:
                        print("Adding parameter:", "Working Temperature", "=",
                              str(resistor_from_partname.working_temperature_range), "into: ", resistor['name'], "@" +
                              resistor['partkeepr_id'].replace("/api/parts/", ""))
                        part = self.partkeepr.get_part(resistor['partkeepr_id'].replace("/api/parts/", ""))
                        part.add_parameter('Working Temperature', resistor_from_partname.working_temperature_range)
                        self.partkeepr.update_part(part)

    def edit_power_parameter(self):
        for resistor in self.resistors:
            if resistor['partkeepr_id'] in skip_autofill.autofill_description:
                print("Skipping parameter update of part: ", resistor['partkeepr_id'], " found in skip list.")
                continue
            if len(resistor['manufacturers']):
                manufacturer_part_number = resistor["manufacturers"][0]['partNumber']
                resistor_from_partname = resistors_partname_decoder.resolve(manufacturer_part_number)
                if resistor_from_partname is not None:
                    resistor_from_parameters = resistor_from_partkeepr_json(resistor)
                    if resistor_from_partname.power != resistor_from_parameters.power:
                        print("Updating power parameter at: ", resistor['partkeepr_id'], "from: ",
                              resistor_from_parameters.power, " to: ", resistor_from_partname.power)
                        new_value = {'value': None,
                                     'minValue': None,
                                     'maxValue': resistor_from_partname.power}
                        self.partkeepr.edit_part_parameter(resistor['partkeepr_id'], "Power", new_value)
