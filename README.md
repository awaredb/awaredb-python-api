# AwareDB: Python API

This is a simple plugin to execute commands on AwareDB. For more information about AwareDB, read [here the full documentation](https://docs.aware-db.com/).

## About AwareDB

AwareDB aims to revolutionize the traditional approach to data by introducing the principle
of **modularity** directly into the **data structure**. While modularity is a well-established
concept in computer science, primarily applied to programming and infrastructure, the realm
of data has remained predominantly static and non-modular,tightly bound to the code
that governs it.

Our innovative approach introduces a groundbreaking concept wherein data becomes **self-aware**.
Individual pieces of data can seamlessly **connect**, **reference one another** through direct links
or employ **mathematical** and **logical operations**. Notably, alterations to one node trigger
**automatic cascading impacts** throughout the system, all achieved without the need for
additional code.

This marks a paradigm shift in data management, empowering a dynamic,
interconnected, and **self-aware data environment**.

## Installation

```bash
$ pip install awaredb
```

## Quick start

```python

from awaredb import AwareDB

# Using token
awaredb = AwareDB(db="<my_db>", token="<my_token>")

# Using username and password
awaredb = AwareDB(db="<my_db>", user="<username>", password="<my_password>")
```

## Read commands

#### calculate

Execute calculations using existing nodes in the database.

Params:
* `formula`: A singular formula or a list of formulas to be computed.
* `states`: A list specifying the active states used during calculations.

Example of a call:

```python
awaredb.calculate(
  formula="${car.power} * 2",
  states=["car.model.x"],
)

# Example of response:
Output: "500 hp"
```

### get

Returns the value of a specific path from nodes in the database.

Params:
* `path`: A single path to be retrieved.
* `states`: A list of states from which data should be retrieved.

Example of a call:

```python
awaredb.get(path="car.power", states=[car.model.x])

# Example of a calculate response
Output: "250 hp"
```


### query

Returns a list of nodes based on the input.

Params:
* `nodes`: List of ids, uids and names from existing nodes.
* `conditions`: A list of conditions that validates if node should be retrieved.
* `properties`: A list of properties that should be retrieve. Defaults to all.
* `states`: A list of states from which data should be retrieved.
* `show_abstract`: If abstract nodes should be retrieved. Defaults to False.

Note: To retrieve all nodes, use `'*'` as `nodes` value.


Example of a call:

```python
awaredb.query(
  nodes=["employee"],
  conditions=["${node.salary.gross} > 60000"],
)

# Example of a calculate response
Output: [
  {
    "id": "7037a8a5-ac2f-4a65-a913-ab1e631fda76"
    "node_type": "employee",
    "name": "John Doe",
    "salary": {
      "gross": "80000"
    },
    "value": {
      "salary": {
        "gross": "80000",
        "net": "56000"
      }
    }
  },
  {
    "id": "7037a8a5-ac2f-4a65-a913-ab1e631fda77"
    "node_type": "employee",
    "name": "Jane Doe",
    "salary": {
      "gross": "100000"
    },
    "value": {
      "salary": {
        "gross": "100000",
        "net": "70000"
      }
    }
  }
]
```


### what_if

Allows to return the impacts of changes without saving them on database.

Params:
* `change`: A dictionary where keys represents paths and values the new values.
* `states`: A list of states from which data should be retrieved.

Example of a call:

```python
awaredb.what_if(
  changes={"battery.capacity": "55 kWh"},
  states=["car.performance"],
)

# Example of a calculate response
Output: {
  "battery.capacity": "55 kWh",
  "car.range": "180 km"
}
```


## Write commands


### flush

Deletes all data currently on database.

Example of a call:

```python
awaredb.flush()
```

### remove

Removes specific nodes and relations from database.

Params:
* `ids`: List of ids from nodes and relations to be deleted.

Example of a call:
```python
awaredb.remove(ids=[
  "7037a8a5-ac2f-4a65-a913-ab1e631fda76",
  "7037a8a5-ac2f-4a65-a913-ab1e631fda77",
])
```

### update

Add and/or updates nodes, relations and relation types from a database.

Params:
* `data`: List of nodes, relations and relation types to created or update.
* `partial`: Updates only passed properties for exiting data. Defaults to False.

Example of a call:

```python
awaredb.update(data=[
  {
    "name": "Fan",
    "mode": {
      "states": {
        "off": ["this.engine.mode.off", "this.lights.status.off"],
        "low": ["this.engine.mode.low", "this.lights.status.on"],
        "mid": ["this.engine.mode.mid", "this.lights.status.on"],
        "high": ["this.engine.mode.high", "this.lights.status.on"]
      }
    },
    "power": "=sum(${this.children.power})",
    "engine": {
      "mode": {"states": ["off", "low", "mid", "high"]},
      "power": {
        "linked-to": "${this.engine.mode}",
        "cases": [
          ["low", "10 W"],
          ["mid", "20 W"],
          ["high", "30 W"],
          ["default", "0 W"]
        ]
      },
      "speed": "=10 rpm * (${this.engine.power} / 1 W)"
    },
    "lights": {
      "status": {"states": ["off", "on"]},
      "power": {
        "linked-to": "this.lights.status",
        "cases": [
          ["off", "0 W"],
          ["on", "5 W"]
        ]
      }
    }
  }
])

# Example of a calculate response
Output: [
    {
      "name": "Fan",
      "mode": {
        "states": {
          "off": ["this.engine.mode.off", "this.lights.status.off"],
          "low": ["this.engine.mode.low", "this.lights.status.on"],
          "mid": ["this.engine.mode.mid", "this.lights.status.on"],
          "high": ["this.engine.mode.high", "this.lights.status.on"]
        }
      },
      "power": "=sum(${this.children.power})",
      "engine": {
        "mode": {"states": ["off", "low", "mid", "high"]},
        "power": {
          "linked-to": "${this.engine.mode}",
          "cases": [
            ["low", "10 W"],
            ["mid", "20 W"],
            ["high", "30 W"],
            ["default", "0 W"]
          ]
        },
        "speed": "=10 rpm * (${this.engine.power} / 1 W)"
      },
      "lights": {
        "status": {"states": ["off", "on"]},
        "power": {
          "linked-to": "this.lights.status",
          "cases": [
            ["off", "0 W"],
            ["on", "5 W"]
          ]
        }
      }
      "value": {
        "mode": {
          "states": {
            "off": ["this.engine.mode.off", "this.lights.status.off"],
            "low": ["this.engine.mode.low", "this.lights.status.on"],
            "mid": ["this.engine.mode.mid", "this.lights.status.on"],
            "high": ["this.engine.mode.high", "this.lights.status.on"]
          }
        },
        "power": {
            "linked-to": "this.engine.mode",
            "cases": [
                [
                    "low",
                    {
                        "linked-to": "this.lights.status",
                        "cases": [
                            ["off", "10.0 W"],
                            ["on", "15.0 W"],
                        ],
                    },
                ],
                [
                    "mid",
                    {
                        "linked-to": "this.lights.status",
                        "cases": [
                            ["off", "20.0 W"],
                            ["on", "25.0 W"],
                        ],
                    },
                ],
                [
                    "high",
                    {
                        "linked-to": "this.lights.status",
                        "cases": [
                            ["off", "30.0 W"],
                            ["on", "35.0 W"],
                        ],
                    },
                ],
                [
                    "default",
                    {
                        "linked-to": "this.lights.status",
                        "cases": [
                            ["off", "0.0 W"],
                            ["on", "5.0 W"],
                        ],
                    },
                ],
            ],
        },
        "engine": {
          "mode": {"states": ["off", "low", "mid", "high"]},
          "power": {
            "linked-to": "${this.engine.mode}",
            "cases": [
              ["low", "10 W"],
              ["mid", "20 W"],
              ["high", "30 W"],
              ["default", "0 W"]
            ]
          },
          "speed": {
              "linked-to": "this.engine.mode",
              "cases": [
                  ["low", "100.0 rpm"],
                  ["mid", "200.0 rpm"],
                  ["high", "300.0 rpm"],
                  ["default", "0.0 rpm"],
              ],
          }
        },
        "lights": {
          "status": {"states": ["off", "on"]},
          "power": {
            "linked-to": "this.lights.status",
            "cases": [
              ["off", "0 W"],
              ["on", "5 W"]
            ]
          }
        }
      }
    }
  ]
```
