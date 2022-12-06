# imports
from datetime import datetime, timedelta
from airflow.decorators import dag,task_group
from airflow.utils.dates import days_ago
from os import getenv
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.providers.amazon.aws.operators.s3_delete_objects import S3DeleteObjectsOperator
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.providers.amazon.aws.operators.s3_list import S3ListOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import pandas as pd
from minio import Minio
from airflow.providers.amazon.aws.operators.s3_copy_object import S3CopyObjectOperator
from sqlalchemy import create_engine


LANDING_ZONE = getenv("LANDING_ZONE", "landing")
LAKEHOUSE = getenv("LAKEHOUSE", "lakehouse")
MINIO = getenv("MINIO", "minio.deepstorage.svc.Cluster.local:8686")
ACCESS_KEY = getenv("ACCESS_KEY", "raat9cl2bEWhbgtQ")
SECRET_ACCESS = getenv("SECRET_ACCESS", "zcJWBrrGkInYEWXf4Oc37tCIdJVeA0fb")
YUGABYTEDB = getenv("YUGABYTEDB", "postgresql://plumber:PlumberSDE@yb-tservers.database.svc.Cluster.local:5433/salesdw")

default_args = {
    'owner': 'vinicius da silva vale',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'email': ['viniciusdvale@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'max_active_run': 1,
    'depends_on_past':False}

description = "DAG to create dim and facts and save in gold and YugabyteDB"

@dag(schedule='@daily', default_args=default_args,catchup=False,
tags=['example','spark','gold','s3','sensor','k8s','YugabyteDB','astrosdk','postgresoperator'],description=description)
def example_gold():
   
    @task_group()
    def dimsalesterritory_gold():
        # use spark-on-k8s to operate against the data
        gold_dimsalesterritory_spark_operator = SparkKubernetesOperator(
        task_id='t_gold_dimsalesterritory_spark_operator',
        namespace='processing',
        application_file='example-dimsalesterritory-gold.yaml',
        kubernetes_conn_id='kubeconnect',
        do_xcom_push=True)

        # monitor spark application using sensor to determine the outcome of the task
        monitor_gold_dimsalesterritory_spark_operator = SparkKubernetesSensor(
        task_id='t_monitor_gold_dimsalesterritory_spark_operator',
        namespace="processing",
        application_name="{{ task_instance.xcom_pull(task_ids='dimsalesterritory_gold.t_gold_dimsalesterritory_spark_operator')['metadata']['name'] }}",
        kubernetes_conn_id="kubeconnect")

        # Confirm files are created
        list_gold_example_dimsalesterritory_folder = S3ListOperator(
        task_id='t_list_gold_example_dimsalesterritory_folder',
        bucket=LAKEHOUSE,
        prefix='gold/example/dimsalesterritory',
        delimiter='/',
        aws_conn_id='minio',
        do_xcom_push=True)

        gold_dimsalesterritory_spark_operator >> monitor_gold_dimsalesterritory_spark_operator >> list_gold_example_dimsalesterritory_folder

    @task_group()
    def dimproductsubcategory_gold():
        # verify if new data has arrived on silver
        verify_dimproductsubcategory_silver = S3KeySensor(
        task_id='t_verify_dimproductsubcategory_silver',
        bucket_name=LAKEHOUSE,
        bucket_key='silver/example/dimproductsubcategory/*.parquet',
        wildcard_match=True,
        timeout=18 * 60 * 60,
        poke_interval=120,
        aws_conn_id='minio')

        # use spark-on-k8s to operate against the data
        gold_dimproductsubcategory_spark_operator = SparkKubernetesOperator(
        task_id='t_gold_dimproductsubcategory_spark_operator',
        namespace='processing',
        application_file='example-dimproductsubcategory-gold.yaml',
        kubernetes_conn_id='kubeconnect',
        do_xcom_push=True)

        # monitor spark application using sensor to determine the outcome of the task
        monitor_gold_dimproductsubcategory_spark_operator = SparkKubernetesSensor(
        task_id='t_monitor_gold_dimproductsubcategory_spark_operator',
        namespace="processing",
        application_name="{{ task_instance.xcom_pull(task_ids='dimproductsubcategory_gold.t_gold_dimproductsubcategory_spark_operator')['metadata']['name'] }}",
        kubernetes_conn_id="kubeconnect")

        # Confirm files are created
        list_gold_example_dimproductsubcategory_folder = S3ListOperator(
        task_id='t_list_gold_example_dimproductsubcategory_folder',
        bucket=LAKEHOUSE,
        prefix='gold/example/dimproductsubcategory',
        delimiter='/',
        aws_conn_id='minio',
        do_xcom_push=True)
        
        verify_dimproductsubcategory_silver >> gold_dimproductsubcategory_spark_operator >> monitor_gold_dimproductsubcategory_spark_operator >> list_gold_example_dimproductsubcategory_folder

    @task_group()
    def dimproductcategory_gold():
        # verify if new data has arrived on silver
        verify_dimproductcategory_silver = S3KeySensor(
        task_id='t_verify_dimproductcategory_silver',
        bucket_name=LAKEHOUSE,
        bucket_key='silver/example/dimproductcategory/*.parquet',
        wildcard_match=True,
        timeout=18 * 60 * 60,
        poke_interval=120,
        aws_conn_id='minio')

        # use spark-on-k8s to operate against the data
        gold_dimproductcategory_spark_operator = SparkKubernetesOperator(
        task_id='t_gold_dimproductcategory_spark_operator',
        namespace='processing',
        application_file='example-dimproductcategory-gold.yaml',
        kubernetes_conn_id='kubeconnect',
        do_xcom_push=True)

        # monitor spark application using sensor to determine the outcome of the task
        monitor_gold_dimproductcategory_spark_operator = SparkKubernetesSensor(
        task_id='t_monitor_gold_dimproductcategory_spark_operator',
        namespace="processing",
        application_name="{{ task_instance.xcom_pull(task_ids='dimproductcategory_gold.t_gold_dimproductcategory_spark_operator')['metadata']['name'] }}",
        kubernetes_conn_id="kubeconnect")

        # Confirm files are created
        list_gold_example_dimproductcategory_folder = S3ListOperator(
        task_id='t_list_gold_example_dimproductcategory_folder',
        bucket=LAKEHOUSE,
        prefix='gold/example/dimproductcategory',
        delimiter='/',
        aws_conn_id='minio',
        do_xcom_push=True)
        
        verify_dimproductcategory_silver >> gold_dimproductcategory_spark_operator >> monitor_gold_dimproductcategory_spark_operator >> list_gold_example_dimproductcategory_folder

    [dimsalesterritory_gold()]
    dimproductcategory_gold() >> dimproductsubcategory_gold()           
dag = example_gold()