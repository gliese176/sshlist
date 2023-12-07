from collections import namedtuple


Settings = namedtuple(
    "Settings", 
    [

    ]
    )


HostData = namedtuple(
    "HostData", 
    [
        "name",
        "host", 
        "port", 
        "username", 
        "key_file"
    ]
    )


EditHostResult = namedtuple(
    "EditHostResult", 
    [
        "aborted", 
        "host_data"
    ]
    )