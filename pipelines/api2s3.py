"""Extract data from an API and upload it to Amazon S3."""
import configparser
import csv
import json
import sys

import boto3
import requests


def load_to_s3(access_key, secret_key, filename):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    s3.upload_file(
        filename,
        bucket_name,
        filename,
    )


if __name__ == "__main__":
    api_response = requests.get("https://lldev.thespacedevs.com/2.2.0/launch/upcoming/")

    response_json = json.loads(api_response.content)

    header = [
        "launch_id",
        "window_start",
        "window_end",
        "provider_name",
        "provider_type",
        "rocket_name",
        "rocket_variant",
        "mission_name",
        "mission_type",
        "pad_name",
        "pad_location",
    ]
    launches = []
    for response in response_json["results"]:
        launch = []
        launch.append(response.get("id", ""))
        launch.append(response.get("window_start", ""))
        launch.append(response.get("window_end", ""))

        service_provider = response.get("launch_service_provider")
        if service_provider:
            launch.append(service_provider.get("name", ""))
            launch.append(service_provider.get("type", ""))
        else:
            launch.extend(["", "", ""])

        rocket_configuration = response["rocket"].get("configuration")
        if rocket_configuration is not None:
            launch.append(rocket_configuration.get("name", ""))
            launch.append(rocket_configuration.get("variant", ""))
        else:
            launch.extend(["", ""])

        mission = response.get("mission")
        if mission:
            launch.append(mission.get("name", ""))
            launch.append(mission.get("type", ""))
        else:
            launch.extend(["", ""])

        launch_pad = response.get("pad")
        if launch_pad:
            launch.append(launch_pad.get("name", ""))
            launch.append(launch_pad.get("map_url", ""))

        launches.append(launch)

    output_file = "upcoming_launches.csv"
    with open(output_file, "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(header)
        writer.writerows(launches)

    parser = configparser.ConfigParser()
    parser.read("pipeline.conf")

    access_key = parser.get("aws_boto_credentials", "access_key")
    secret_key = parser.get("aws_boto_credentials", "secret_key")
    bucket_name = parser.get("aws_boto_credentials", "bucket_name")

    load_to_s3(access_key, secret_key, output_file)
