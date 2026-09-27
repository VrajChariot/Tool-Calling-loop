SUBSTATIONS = {
    "neuenhagen":  {"id": "SS-001", "name": "Neuenhagen",  "region": "Brandenburg"},
    "wolmirstedt": {"id": "SS-002", "name": "Wolmirstedt", "region": "Sachsen-Anhalt"},
}
LOADS = {"SS-001": 1240.5, "SS-002": 880.0}
def get_substations(name: str):
    """
    Get the list of substations for a given namespace.

    Args:
        namespace (str): The namespace to retrieve substation for.
    """
    normalized_name = name.strip().lower()
    value = SUBSTATIONS.get(normalized_name)
    if value is None:
        return {"error": f"unknown substation: {name}"}
    else:
        return (value)

get_substations("wolmirstedt")

def get_load(substation_id : str):
    """
    Get load of an inidividual substation using substation id

    Args:
        substation_id(str): the id to retrive load of a substation.
    """
    normalized_id = substation_id.strip().upper()
    load = LOADS.get(normalized_id)
    if load is None:
        return {"error": f"unknown substation_id: {substation_id}"}
    else:
        return {"substation_id": normalized_id, "load_mw": load}
