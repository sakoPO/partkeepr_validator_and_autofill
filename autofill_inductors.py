import configparser
import json
from partkeepr_connector.partkeepr import Partkeepr
from partkeepr_connector.part_to_component import part_to_inductor
import sys

sys.path.insert(1, "third_party/partname-resolver")
from partname_resolver.inductors import inductors_partname_decoder


class AutoFillInductors:
    def __init__(self, config_filename="config.ini"):
        config = configparser.ConfigParser()
        config.read(config_filename)
        self.partkeepr = Partkeepr(config)

    def add_missing_parameters(self, part, inductor):
        if not part.has_parameter("Part Type") and inductor.type is not None:
            part.add_parameter("Part Type", inductor.type.value)
        if not part.has_parameter('Inductance') and inductor.inductance is not None:
            part.add_parameter('Inductance', inductor.inductance)
        if not part.has_parameter('Tolerance') and inductor.tolerance is not None:
            part.add_parameter('Tolerance', inductor.tolerance)
        if not part.has_parameter('Working Temperature') and inductor.working_temperature_range is not None:
            part.add_parameter('Working Temperature', inductor.working_temperature_range)
        if not part.has_parameter("Voltage") and inductor.max_working_voltage is not None:
            part.add_parameter("Voltage", inductor.max_working_voltage, numeric_value_field='maxVoltage')
        if not part.has_parameter('Q') and inductor.q is not None:
            part.add_parameter('Q', inductor.q)
        if not part.has_parameter('Resistance') and inductor.dc_resistance:
            part.add_parameter("Resistance", inductor.resistance)
        if not part.has_parameter('Rated Current') and inductor.rated_current:
            part.add_parameter('Rated Current', inductor.rated_current)
        if not part.has_parameter("Self Resonant Frequency") and inductor.self_resonant_frequency:
            part.add_parameter('Self Resonant Frequency', inductor.self_resonant_frequency)
        return part

    def update_description(self, part, description):
        if description is not None:
            print('\tNew description:', description)
            part.set_description(description)
        return part

    def update_comment(self, part, comment):
        if comment is not None and len(comment) > 0:
            print('\tNew comment:', comment)
            part.set_comment(comment)
        return part

    def run(self, part_list, dry_run=False):
        for part_id in part_list:
            part = self.partkeepr.get_part(part_id)
            inductor_form_parameters = part_to_inductor(part)
            if len(part.get_manufacturers()) != 1:
                print("Unable to update parameters of:", part.get_name(), "(" + part.get_id() + "),", "reason: incorrect manufacturers count")
                print("\tUpdating description only")
                part = self.update_description(part, inductor_form_parameters.get_description())
            else:
                inductor = inductors_partname_decoder.resolve(part.get_manufacturers()[0]['partNumber'])
                if inductor is not None:
                    print("Updating:", part.get_name(), "(" + part.get_id() + "),")
                    inductor.merge(inductor_form_parameters)
                    part = self.add_missing_parameters(part, inductor)
                    part = self.update_description(part, inductor.get_description())
                    part = self.update_comment(part, inductor.note)
                else:
                    print("Unable to update parameters of:", part.get_name(), "(" + part.get_id() + "),",
                          "reason: unable to decode manufacturer part number")
                    print("\tUpdating description only")
                    part = self.update_description(part, inductor_form_parameters.get_description())
            if dry_run:
                print(json.dumps(part.request, indent=4, sort_keys=True))
            else:
                self.partkeepr.update_part(part)









