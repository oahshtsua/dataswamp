"""Extract data from a PostgreSQL table and upload it to Amazon S3."""
import configparser
import csv

import boto3
import psycopg2


def extract_to_csv(connection, query=None, filename=None):
    query = query if query else "SELECT * FROM orders;"
    filename = filename if filename else "db_extract.csv"

    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    with open(filename, "w") as fp:
        writer = csv.writer(fp)
        writer.writerows(results)

    cursor.close()


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
    parser = configparser.ConfigParser()
    parser.read("pipeline.conf")

    db_name = parser.get("postgres_config", "database")
    db_user = parser.get("postgres_config", "user")
    db_password = parser.get("postgres_config", "password")
    db_host = parser.get("postgres_config", "host")
    db_port = parser.get("postgres_config", "port")

    access_key = parser.get("aws_boto_credentials", "access_key")
    secret_key = parser.get("aws_boto_credentials", "secret_key")
    bucket_name = parser.get("aws_boto_credentials", "bucket_name")

    output_file = "extracted_sales.csv"

    conn = psycopg2.connect(
        f"dbname={db_name} user={db_user} password={db_password} host={db_host}",
        port=db_port,
    )

    extract_to_csv(conn, filename="extracted_orders.csv")
    load_to_s3(access_key, secret_key, output_file)

    conn.close()
