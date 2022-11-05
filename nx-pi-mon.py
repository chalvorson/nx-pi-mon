"""nx-pi-mon.py - NetXMS Agent PI Monitor

Dependencies:
    PIconnect: Tested with 0.9.1        (pip install PIconnect)
    PI AF SDK: Tested with 2.10.9.253
"""
import argparse
import subprocess

import PIconnect as PI
from PIconnect.PIData import PISeries

def_duration = 5
def_tag = "SINUSOID"
def_param = ""
nxapush = "C:\\NetXMS\\bin\\nxapush.exe"


def is_changing(data: PISeries) -> bool:
    """is_changing - determines if the data in the PISeries is changing.

    Args:
        data (PISeries): the PI data to test

    Returns:
        bool: True if the data has more than one unique value, otherwise false.
    """
    unique_data = set()
    for point in data:
        unique_data.add(point)
        if len(unique_data) > 1:
            return True

    return False


def main():
    # Allow the user to specify the PI tag and the duration to check.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--tag", type=str, required=True, help="PI tag to query for staleness or value"
    )
    parser.add_argument(
        "-p",
        "--param",
        type=str,
        required=False,
        help="NetXMS parameter name receiving pushed value",
    )

    # Stale check options
    parser.add_argument(
        "-s",
        "--stale",
        action=argparse.BooleanOptionalAction,
        help="Check PI tag for staleness",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=def_duration,
        help="Duration, in minutes, of data to check for staleness",
    )

    parser.add_argument(
        "-n",
        "--nopush",
        action=argparse.BooleanOptionalAction,
        help="Don't push anything to NetXMS",
    )

    args = parser.parse_args()

    # If param is defined, push the param name else push the tag name?
    if args.param is None:
        param = args.tag
    else:
        param = args.param

    try:
        pivalue = ""
        # Connect to the default server and query for the tag's data in the specified range
        with PI.PIServer(timeout=30) as server:
            # Select the first matching tag to query
            health_point = server.search(args.tag)
            if len(health_point) > 0:
                health_point = health_point[0]
            else:
                print("Error: Unable to find PI Tag.")
                exit(-1)

            # If we want staleness, check for staleness.  Otherwise, retieve the current value.
            if args.stale:
                series = health_point.recorded_values(f"*-{args.duration}m", "*")
                pivalue = is_changing(series)
            else:
                series = health_point.current_value
                pivalue = series

    except Exception as e:
        print(f"Error: {e}")
        exit(-2)

    try:
        if not args.nopush:
            # Use the NetXMS nxapush binary to send the status to the NetXMS server
            subprocess.run([nxapush, f"{param}={pivalue}"])
        else:
            print(f"Tag: {args.tag}   nxapush {param}={pivalue}")

    except Exception as e:
        print(f"Error: {e}")
        exit(-3)


if __name__ == "__main__":
    main()
