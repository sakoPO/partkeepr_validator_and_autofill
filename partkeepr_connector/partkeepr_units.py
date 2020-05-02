from decimal import Decimal

class Units:
    def __init__(self, units):
        self.units = units

    def get(self, name):
        for unit in self.units:
            if name == unit['name']:
                return unit

    def get_supported_prefixes(self, unit):
        prefixes_names = []
        prefixes_multipliers = []
        for prefix in unit['prefixes']:
            prefixes_names.append(prefix['prefix'] if prefix['prefix'] != '-' else unit['symbol'])
            prefixes_multipliers.append(Decimal(prefix['base'] ** Decimal(prefix['exponent'])))
        return {"names": prefixes_names, 'multipliers': prefixes_multipliers}

    def get_prefix(self, unit, prefix_name):
        for prefix in unit['prefixes']:
            if prefix['prefix'] == prefix_name:
                return prefix
